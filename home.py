
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from db import db, users_collection, designs_collection
import base64
from openai import OpenAI
import os
from dotenv import load_dotenv
from db import reviews_collection

load_dotenv()
home_bp = Blueprint('home_bp', __name__)

client = OpenAI(
    base_url="https://api.studio.nebius.com/v1/",
    api_key=os.getenv("api_key")
)

@home_bp.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    generated_image = None
    design_specs = None

    if request.method == 'POST':
        design_data = {
            'username': current_user.username,
            'apartment_size': request.form.get('apartment_size'),
            'bedrooms': request.form.get('bedrooms'),
            'bathrooms': request.form.get('bathrooms'),
            'master_features': request.form.getlist('master_features'),
            'living_room_style': request.form.get('living_room_style'),
            'kitchen_style': request.form.get('kitchen_style'),
            'floor_material': request.form.get('floor_material'),
            'wall_material': request.form.get('wall_material'),
            'color_scheme': request.form.get('color_scheme'),
            'lighting_style': request.form.get('lighting_style'),
            'arch_style': request.form.get('arch_style'),
            'special_requests': request.form.get('special_requests')
        }

        # Build detailed prompt
        prompt = f"""Create a photorealistic 3D isometric floor plan with these specifications:
        
        Apartment Type: {design_data['apartment_size']} apartment
        Architectural Style: {design_data['arch_style']}
        
        Bedrooms: {design_data['bedrooms']} (Master with: {', '.join(design_data['master_features']) if design_data['master_features'] else 'standard features'})
        Bathrooms: {design_data['bathrooms']} (Modern fixtures with {design_data['wall_material']} walls)
        
        Living Room: {design_data['living_room_style']} style with appropriate furniture
        Kitchen: {design_data['kitchen_style']} style with modern appliances
        
        Materials:
        - Floors: {design_data['floor_material']}
        - Walls: {design_data['wall_material']}
        
        Color Scheme: {design_data['color_scheme']}
        Lighting: {design_data['lighting_style']} creating a warm ambiance
        
        Special Requests: {design_data['special_requests'] or 'None'}
        """

        try:
            response = client.images.generate(
                model="black-forest-labs/flux-schnell",
                prompt=prompt,
                response_format="b64_json",
                extra_body={
                    "response_extension": "png",
                    "width": 1200,
                    "height": 1200,
                    "num_inference_steps": 6,
                    "negative_prompt": "blurry, low quality, unrealistic proportions",
                    "seed": -1
                }
            )

            b64_data = response.data[0].b64_json
            generated_image = f"data:image/png;base64,{b64_data}"

            design_doc = {
                "user_id": current_user.id,
                "username": current_user.username,
                "image_data": generated_image,
                "design_specs": prompt,
                **design_data  # Include all design_data fields directly in the document
            }

            designs_collection.insert_one(design_doc)

        except Exception as e:
            print("Image generation failed:", str(e))
            generated_image = None

    # Get user designs with all fields we need for display
    user_designs = list(designs_collection.find(
        {"user_id": current_user.id},
        {
            "image_data": 1,
            "apartment_size": 1,
            "bedrooms": 1,
            "bathrooms": 1,
            "arch_style": 1,
            "_id": 0
        }
    ).sort("_id", -1).limit(10))

    return render_template(
        "home.html",
        username=current_user.username,
        image_data=generated_image,
        user_designs=user_designs
    )



from flask import Blueprint, render_template, request, redirect
from db import reviews_collection

review_bp = Blueprint('review_bp', __name__)

# Route to display all reviews
@review_bp.route('/reviews')
def view_reviews():
    all_reviews = list(reviews_collection.find())
    return render_template('view_reviews.html', reviews=all_reviews)

# Route to submit a review
@review_bp.route('/submit_review', methods=['POST'])
def submit_review():
    review_text = request.form['review']
    if review_text.strip():
        reviews_collection.insert_one({'text': review_text})
    return redirect('/reviews')
