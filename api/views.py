import os
import logging
from PIL import Image
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import MarineSpecies
from .serializers import MarineSpeciesSerializer
from .ai_handler import AIHandler
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Initialize logger for debugging
logger = logging.getLogger(__name__)

# Directory to save uploaded images
UPLOAD_DIR = 'uploads/'
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize AIHandler
model_path = "model/resnet50_model_finetuned.pth"
class_to_idx_path = "model/class_to_idx.json"
try:
    ai_handler = AIHandler(model_path, class_to_idx_path)
    logger.info("AIHandler initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize AIHandler: {e}")


@api_view(['POST'])
def upload_image(request):
    """
    Upload an image or update the prompt for an existing image.
    """
    try:
        image_file = request.FILES.get('image')
        prompt = request.POST.get('prompt', '').strip()
        image_id = request.POST.get('image_id')  # For updating prompt

        # Validate inputs
        if not image_file and not image_id:
            logger.error("No image or image ID provided.")
            return JsonResponse({'error': 'Either an image or image ID is required'}, status=400)

        if not prompt:
            logger.error("No prompt provided.")
            return JsonResponse({'error': 'Prompt is required'}, status=400)

        if image_file:
            # New image upload
            last_entry = MarineSpecies.objects.last()
            new_image_id = str(int(last_entry.image_id) + 1) if last_entry else "1"
            logger.info(f"Generated Image ID: {new_image_id}")

            image_path = os.path.join(MEDIA_ROOT, 'uploads', f"{new_image_id}.jpg")
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            with open(image_path, 'wb') as f:
                for chunk in image_file.chunks():
                    f.write(chunk)

            try:
                image = Image.open(image_path)
            except Exception as e:
                logger.error(f"Failed to open image: {e}")
                return JsonResponse({'error': f'Failed to open image: {e}'}, status=400)

            classification = ai_handler.classify(image)
            if "error" in classification:
                logger.error(f"Classification error: {classification['error']}")
                return JsonResponse({'error': classification["error"]}, status=500)

            class_name = classification["class_name"]
            species_data = ai_handler.retrieve_data(class_name)

            species_entry = MarineSpecies.objects.create(
                image_id=new_image_id,
                class_name=class_name,
                image=image_file,
                summary=species_data.get('summary', 'No summary available'),
                url=species_data.get('url', 'No URL available'),
                prompt=prompt
            )
            logger.info(f"Saved entry to database for Image ID: {new_image_id}")

            return JsonResponse({
                'image_id': species_entry.image_id,
                'summary': species_entry.summary,
                'url': species_entry.url,
                'prompt': species_entry.prompt
            }, status=201)

        elif image_id:
            # Update the prompt for an existing image
            try:
                species_entry = MarineSpecies.objects.get(image_id=image_id)
                species_entry.prompt = prompt

                # Reprocess the image and update the summary
                classification = ai_handler.classify(Image.open(species_entry.image.path))
                if "error" in classification:
                    logger.error(f"Classification error during prompt update: {classification['error']}")
                    return JsonResponse({'error': classification["error"]}, status=500)

                class_name = classification["class_name"]
                species_data = ai_handler.retrieve_data(class_name)
                species_entry.summary = species_data.get('summary', 'No summary available')
                species_entry.url = species_data.get('url', 'No URL available')
                species_entry.save()

                logger.info(f"Updated prompt and summary for Image ID: {image_id}")

                return JsonResponse({
                    'message': f'Prompt updated successfully for Image ID: {image_id}',
                    'image_id': species_entry.image_id,
                    'prompt': species_entry.prompt,
                    'summary': species_entry.summary,
                    'url': species_entry.url
                }, status=200)

            except MarineSpecies.DoesNotExist:
                logger.error(f"Image ID not found: {image_id}")
                return JsonResponse({'error': 'Image ID not found'}, status=404)

    except Exception as e:
        logger.error(f"Unexpected error in upload_image: {e}")
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)


@api_view(['GET', 'DELETE'])
def history(request):
    """
    View or delete the history of classified images.
    """
    try:
        if request.method == 'GET':
            species_entries = MarineSpecies.objects.all().order_by('-image_id')
            serializer = MarineSpeciesSerializer(species_entries, many=True)
            logger.info(f"Retrieved {len(species_entries)} history entries.")
            return JsonResponse(serializer.data, safe=False, status=200)

        elif request.method == 'DELETE':
            image_id = request.data.get('image_id')
            if not image_id:
                logger.error("No Image ID provided for deletion.")
                return JsonResponse({'error': 'Image ID is required for deletion'}, status=400)

            try:
                species_entry = MarineSpecies.objects.get(image_id=image_id)
                os.remove(species_entry.image.path)  # Delete the associated image file
                species_entry.delete()
                logger.info(f"Deleted entry and file for Image ID: {image_id}")
                return JsonResponse({'message': f'Image {image_id} deleted successfully'}, status=200)
            except MarineSpecies.DoesNotExist:
                logger.error(f"Image ID not found: {image_id}")
                return JsonResponse({'error': 'Image ID not found'}, status=404)

    except Exception as e:
        logger.error(f"Unexpected error in history endpoint: {e}")
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)


def home(request):
    """
    Home endpoint for the API.
    """
    logger.info("Home endpoint accessed.")
    return JsonResponse({'message': 'Welcome to the OceanID API!'}, status=200)
