import os
import cv2
import numpy as np
from PIL import Image
import pytesseract
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Sum
from .models import ReceiptUpload, Expense, Notification, Budget


def notify_user(user, title, message):
    """Create a notification in the database for the user"""
    print(f"Creating notification for {user.username}: {title} - {message}")
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message
    )
    print(f"Notification created with ID: {notification.id}")
    return notification


@receiver(post_save, sender=ReceiptUpload)
def process_receipt_ocr(sender, instance, created, **kwargs):
    if created and instance.image:
        try:
            image_path = instance.image.path

            # Step 1: Load the image using OpenCV
            img = cv2.imread(image_path)

            # Step 2: Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Step 3: Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)

            # Step 4: Apply Otsu's thresholding to binarize
            _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Step 5: Apply morphological operations to clean noise
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

            # Step 6: Invert the image (text should be black on white)
            inverted = cv2.bitwise_not(cleaned)

            # Step 7: Save to a temporary path (with original extension)
            base, ext = os.path.splitext(image_path)
            temp_path = f"{base}_preprocessed{ext}"
            cv2.imwrite(temp_path, inverted)

            # Step 8: OCR using pytesseract with --psm 6
            custom_config = r'--oem 3 --psm 6'
            extracted_text = pytesseract.image_to_string(Image.open(temp_path), config=custom_config)

            # Step 9: Save OCR text to the model
            instance.ocr_text = extracted_text
            print(f"Extracted Text: {extracted_text}")
            instance.save(update_fields=["ocr_text"])

            # Optional: Clean up the temporary image
            if os.path.exists(temp_path):
                os.remove(temp_path)

        except Exception as e:
            print(f"OCR Processing Error: {e}")



@receiver(post_save, sender=Expense)
def expense_notification(sender, instance, created, **kwargs):
    user = instance.owner
    
    if created:
        # 1. Notify user of new expense
        notify_user(
            user,
            title="New Expense Added",
            message=f"You just added an expense of ₹{instance.amount} under {instance.category}.",
        )

        # 2. Check budget overrun - using Budget model instead of Profile
        month = timezone.now().month
        year = timezone.now().year
        
        budget = Budget.objects.filter(owner=user).first()
        if budget:
            total_monthly_expense = Expense.objects.filter(
                owner=user, date__month=month, date__year=year
            ).aggregate(total=Sum('amount'))['total'] or 0

            if total_monthly_expense > budget.amount:
                notify_user(
                    user,
                    title="⚠️ Budget Limit Exceeded",
                    message=f"Your total expenses this month (₹{total_monthly_expense}) have exceeded your budget (₹{budget.amount}).",
                )
    else:  # This will only trigger for updates, not creation
        notify_user(
            user,
            title="Expense Updated",
            message=f"Your expense for {instance.content} has been updated to ₹{instance.amount}."
        )

from django.db.models.signals import post_delete

@receiver(post_delete, sender=Expense)
def expense_delete_notification(sender, instance, **kwargs):
    notify_user(
        instance.owner,
        title="Expense Deleted",
        message=f"Your expense of ₹{instance.amount} for {instance.content} has been deleted."
    )

# Budget-related notifications
@receiver(post_save, sender=Budget)
def budget_notification(sender, instance, created, **kwargs):
    if created:
        notify_user(
            instance.owner,
            title="Budget Created",
            message=f"You've set a new budget of ₹{instance.amount}."
        )
    else:
        notify_user(
            instance.owner,
            title="Budget Updated",
            message=f"Your budget has been updated to ₹{instance.amount}."
        )

@receiver(post_delete, sender=Budget)
def budget_delete_notification(sender, instance, **kwargs):
    notify_user(
        instance.owner,
        title="Budget Deleted",
        message=f"Your budget of ₹{instance.amount} has been deleted."
    )