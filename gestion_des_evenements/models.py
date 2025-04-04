from django.db import models
import datetime
import os

# Helper function to generate a unique file path
def file_path(instance, filename):
    timenow = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # Safe filename creation
    filename = f"{timenow}_{filename}"
    return os.path.join('uploads', filename)

class TodoItem(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, max_length=500)
    image = models.ImageField(upload_to=file_path, null=True, blank=True)
