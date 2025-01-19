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
try:
    ai_handler = AIHandler()
    logger.info("AIHandler initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize AIHandler: {e}")


@api_view(['POST'])
def upload_image(request):
    """
    Upload an image and process it to generate a description.
    """
    try:
        image_file = request.FILES.get('image')

        # Validate input
        if not image_file:
            logger.error("No image provided.")
            return JsonResponse({'error': 'An image file is required'}, status=400)

        try:
            # Open the image and generate a description
            pil_image = Image.open(image_file)
            description, error = ai_handler.describe_image(pil_image, None)

            if error:
                logger.error(f"Error in image description: {error}")
                return JsonResponse({'error': error}, status=500)

            # Save the image and data in the database
            species_entry = MarineSpecies(
                class_name="Described Image",
                image=image_file,
                summary=description
            )
            species_entry.save()  # Save the object to the database

            logger.info(f"Saved entry to database for Image ID: {species_entry.image_id}")

            return JsonResponse({
                'image_id': species_entry.image_id,
                'summary': species_entry.summary
            }, status=201)

        except Exception as e:
            logger.error(f"Unexpected error during image upload: {e}")
            return JsonResponse({'error': 'Failed to process the image.'}, status=500)

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
