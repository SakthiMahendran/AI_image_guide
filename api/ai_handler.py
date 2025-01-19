from huggingface_hub import InferenceClient
from PIL import Image
import io

API_KEY = "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"

class AIHandler:
    def __init__(self):
        # Initialize the Hugging Face Image-to-Text model with InferenceClient
        self.image_model_id = "Salesforce/blip-image-captioning-base"
        self.inference_client = InferenceClient(model=self.image_model_id, token=API_KEY)

    def describe_image(self, image, query=None):
        """
        Use the Hugging Face Image-to-Text model to describe an image based on a query.

        Parameters:
        image (PIL.Image.Image): The input image to describe.
        query (str): An optional query to guide the description.

        Returns:
        tuple: A tuple containing the description (str) and an error message (str, if any).
        """
        try:
            # Convert the PIL image to a byte array
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")  # Save as PNG format
            image_bytes = buffered.getvalue()

            # Send the image to the Hugging Face model
            # Note: The query is not directly used because `image_to_text` does not accept such a parameter
            response = self.inference_client.image_to_text(image=image_bytes)

            # Extract the description from the response
            description = response.get("generated_text", "No description available")
            return description, None
        except Exception as e:
            return None, str(e)
