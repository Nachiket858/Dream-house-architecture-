

# from flask import Blueprint, render_template, request, redirect, url_for, session
# from flask_login import login_required, current_user
# from db import db, users_collection
# import base64
# from openai import OpenAI
# from PIL import Image
# from io import BytesIO
# from datetime import datetime

# home_bp = Blueprint('home_bp', __name__)

# # OpenAI Client Setup
# api_key = "eyJhbGciOiJIUzI1NiIsImtpZCI6IlV6SXJWd1h0dnprLVRvdzlLZWstc0M1akptWXBvX1VaVkxUZlpnMDRlOFUiLCJ0eXAiOiJKV1QifQ.eyJzdWIiOiJnb29nbGUtb2F1dGgyfDEwMzUxODUzOTkzMjQ1OTA0OTQ4NiIsInNjb3BlIjoib3BlbmlkIG9mZmxpbmVfYWNjZXNzIiwiaXNzIjoiYXBpX2tleV9pc3N1ZXIiLCJhdWQiOlsiaHR0cHM6Ly9uZWJpdXMtaW5mZXJlbmNlLmV1LmF1dGgwLmNvbS9hcGkvdjIvIl0sImV4cCI6MTkwNjcwNjU2OCwidXVpZCI6ImUwZWRlNzU5LTgwZGYtNDE2Yi1iNTg4LTYwMTgxZDAzODdlZCIsIm5hbWUiOiJkaGEiLCJleHBpcmVzX2F0IjoiMjAzMC0wNi0wM1QwODo0Mjo0OCswMDAwIn0.F1NxKPImHBSmQ7W5uENvZcQKZX5TjfsYmjdFZoGbaJE"
# # api_key = "eyJhbGciOiJIUzI1NiIsImtpZCI6IlV6SXJWd1h0dnprLVRvdzlLZWstc0M1akptWXBvX1VaVkxUZlpnMDRlOFUiLCJ0eXAiOiJKV1QifQ..."
# client = OpenAI(
#     base_url="https://api.studio.nebius.com/v1/",
#     api_key=api_key
# )

# @home_bp.route('/home', methods=['GET', 'POST'])
# @login_required
# def home():
#     generated_image = None

#     if request.method == 'POST':
#         design_data = {
#             'username': current_user.username,
#             'area': request.form.get('area'),
#             'style': request.form.get('style'),
#             'bedrooms': request.form.get('bedrooms'),
#             'bathrooms': request.form.get('bathrooms'),
#             'floors': request.form.get('floors'),
#             'garden': request.form.get('garden'),
#             'balcony': request.form.get('balcony'),
#             'created_at': datetime.utcnow()
#         }

#         prompt = (
#             f"Create a 2D architectural design of a {design_data['style']} style house "
#             f"with {design_data['bedrooms']} bedrooms, {design_data['bathrooms']} bathrooms, "
#             f"{design_data['floors']} floors, total area {design_data['area']} sq ft, "
#             f"{'with' if design_data['balcony'] == 'yes' else 'without'} balcony and "
#             f"{design_data['garden']} sq ft garden."
#         )

#         try:
#             response = client.images.generate(
#                 model="black-forest-labs/flux-schnell",
#                 prompt=prompt,
#                 response_format="b64_json",
#                 extra_body={
#                     "response_extension": "png",
#                     "width": 1024,
#                     "height": 1024,
#                     "num_inference_steps": 4,
#                     "negative_prompt": "",
#                     "seed": -1
#                 }
#             )

#             # Get image in base64
#             b64_data = response.data[0].b64_json
#             generated_image = f"data:image/png;base64,{b64_data}"

#             # Save to MongoDB
#             design_data['image_b64'] = b64_data  # Only base64 string, without prefix
#             db['designs'].insert_one(design_data)  # Using a new 'designs' collection

#         except Exception as e:
#             print("Image generation failed:", str(e))
#             generated_image = None

#         return render_template("home.html", username=current_user.username, image_data=generated_image)

#     return render_template("home.html", username=current_user.username, image_data=None)


from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from db import db, users_collection, designs_collection
import base64
from openai import OpenAI

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key
api_key = os.getenv("api_key")




home_bp = Blueprint('home_bp', __name__)

# api_key = "your_actual_api_key"
# api_key = "eyJhbGciOiJIUzI1NiIsImtpZCI6IlV6SXJWd1h0dnprLVRvdzlLZWstc0M1akptWXBvX1VaVkxUZlpnMDRlOFUiLCJ0eXAiOiJKV1QifQ.eyJzdWIiOiJnb29nbGUtb2F1dGgyfDEwMzUxODUzOTkzMjQ1OTA0OTQ4NiIsInNjb3BlIjoib3BlbmlkIG9mZmxpbmVfYWNjZXNzIiwiaXNzIjoiYXBpX2tleV9pc3N1ZXIiLCJhdWQiOlsiaHR0cHM6Ly9uZWJpdXMtaW5mZXJlbmNlLmV1LmF1dGgwLmNvbS9hcGkvdjIvIl0sImV4cCI6MTkwNjcwNjU2OCwidXVpZCI6ImUwZWRlNzU5LTgwZGYtNDE2Yi1iNTg4LTYwMTgxZDAzODdlZCIsIm5hbWUiOiJkaGEiLCJleHBpcmVzX2F0IjoiMjAzMC0wNi0wM1QwODo0Mjo0OCswMDAwIn0.F1NxKPImHBSmQ7W5uENvZcQKZX5TjfsYmjdFZoGbaJE"
client = OpenAI(
    base_url="https://api.studio.nebius.com/v1/",
    api_key=api_key
)


# print(api_key)
@home_bp.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    generated_image = None

    if request.method == 'POST':
        design_data = {
            'username': current_user.username,
            'area': request.form.get('area'),
            'style': request.form.get('style'),
            'bedrooms': request.form.get('bedrooms'),
            'bathrooms': request.form.get('bathrooms'),
            'floors': request.form.get('floors'),
            'garden': request.form.get('garden'),
            'balcony': request.form.get('balcony')
        }

        prompt = (
            f"Create a 2D architectural design of a {design_data['style']} style house "
            f"with {design_data['bedrooms']} bedrooms, {design_data['bathrooms']} bathrooms, "
            f"{design_data['floors']} floors, total area {design_data['area']} sq ft, "
            f"{'with' if design_data['balcony'] == 'yes' else 'without'} balcony and "
            f"{design_data['garden']} sq ft garden."
        )

        try:
            response = client.images.generate(
                model="black-forest-labs/flux-schnell",
                prompt=prompt,
                response_format="b64_json",
                extra_body={
                    "response_extension": "png",
                    "width": 1024,
                    "height": 1024,
                    "num_inference_steps": 4,
                    "negative_prompt": "",
                    "seed": -1
                }
            )

            b64_data = response.data[0].b64_json
            generated_image = f"data:image/png;base64,{b64_data}"

            # Save image with user ID
            designs_collection.insert_one({
                "user_id": current_user.id,
                "username": current_user.username,
                "image_data": generated_image
            })

        except Exception as e:
            print("Image generation failed:", str(e))
            generated_image = None

    # Fetch only current user's images
    user_images_cursor = designs_collection.find({"user_id": current_user.id})
    user_images = [doc["image_data"] for doc in user_images_cursor]

    return render_template("home.html", username=current_user.username, image_data=generated_image, user_images=user_images)





