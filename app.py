from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
import ee
import json
from datetime import datetime, timedelta
import uuid
import os
from pymongo import MongoClient
import certifi

app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')
app.secret_key = 'vriddhi_super_secret_session_key_987'
CORS(app)

# 1. Connect to MongoDB Atlas
MONGO_URI = "mongodb+srv://sunlightedsky7239_db_user:5hu6rjoTezOHu0wV@cluster0.dbbcipx.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["agriculture_app"]
users_col = db["farmer_profiles"]
history_col = db["fields_telemetry"]
marketplace_col = db["marketplace_items"]
claims_col = db["insurance_claims"]
orders_col = db["marketplace_orders"]

# Initialize a dummy user document if the database collection is empty
DUMMY_FARMER_ID = 101
if not users_col.find_one({"farmer_id": DUMMY_FARMER_ID}):
    users_col.insert_one({
        "farmer_id": DUMMY_FARMER_ID,
        "name": "anchu",
        "district": "kamrup",
        "credit_points": 0  # Starts at 0 credits as requested
    })

# Seed default items in marketplace_items if the collection is empty
if marketplace_col.count_documents({}) == 0:
    marketplace_col.insert_many([
        {
            "id": "med-1",
            "title": "Neem Shield Bio-Pesticide",
            "type": "medicine",
            "description": "100% cold-pressed organic neem oil formulation for organic insect and pest control.",
            "price": 299.00,
            "image_url": "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?auto=format&fit=crop&w=400&q=80",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": "med-2",
            "title": "Trichoderma Fungicide",
            "type": "medicine",
            "description": "Bio-fungicide shielding crops against root rot, wilt, and damping-off disease.",
            "price": 249.00,
            "image_url": "https://images.unsplash.com/photo-1592417817098-8f3d6eb19675?auto=format&fit=crop&w=400&q=80",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": "med-3",
            "title": "Premium Plant Growth Stimulant",
            "type": "medicine",
            "description": "Concentrated seaweed extract powder boosting photosynthesis and root growth.",
            "price": 399.00,
            "image_url": "https://images.unsplash.com/photo-1530595467537-0b5996c41f2d?auto=format&fit=crop&w=400&q=80",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": "ess-1",
            "title": "Enriched Soil Vermicompost",
            "type": "essential",
            "description": "Pure worm-castings packed with microbial activity and vital trace nutrients.",
            "price": 180.00,
            "image_url": "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=400&q=80",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": "ess-2",
            "title": "Micro Drip Irrigation System",
            "type": "essential",
            "description": "Adjustable emitters and drip lines for precise, water-saving root irrigation.",
            "price": 899.00,
            "image_url": "https://images.unsplash.com/photo-1563514227147-6d2ff665a6a0?auto=format&fit=crop&w=400&q=80",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": "ess-3",
            "title": "Dynamic Soil pH Tester",
            "type": "essential",
            "description": "High-accuracy analog probe to gauge pH, moisture levels, and ambient sunlight.",
            "price": 450.00,
            "image_url": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=400&q=80",
            "created_at": datetime.utcnow().isoformat()
        }
    ])

def force_ee_initialization():
    """Bulletproof Earth Engine initialization engine for cloud deployments."""
    try:
        if ee.data.is_initialized():
            return True
    except Exception:
        pass
        
    raw_key = os.getenv('EARTHENGINE_SERVICE_ACCOUNT_KEY')
    if raw_key:
        try:
            # Check if environment variable is passed parsed as a dict map object
            if isinstance(raw_key, dict):
                key_data = raw_key
            else:
                # Process clean string execution logic mappings safely
                raw_key = raw_key.strip()
                if raw_key.startswith("'") and raw_key.endswith("'"): raw_key = raw_key[1:-1]
                if raw_key.startswith('"') and raw_key.endswith('"'): raw_key = raw_key[1:-1]
                key_data = json.loads(raw_key)
            
            credentials = ee.ServiceAccountCredentials(key_data['client_email'], key_data)
            ee.Initialize(credentials, project=key_data['project_id'])
            print("======> GEE initialized successfully via Service Account! <======")
            return True
        except Exception as e:
            print(f"❌ CRITICAL GEE AUTH FAILURE DETECTED: {str(e)}")
            return False
    else:
        try:
            ee.Initialize()
            print("======> GEE initialized successfully via local context credentials! <======")
            return True
        except Exception as e:
            print("======> GEE Local Initialization Fallback Failed! Error:", str(e))
            return False

# Run initialization engine once at global instance start setup sequence
force_ee_initialization()

@app.route('/api/farmer-stats', methods=['GET'])
def get_farmer_stats():
    """Endpoint to fetch the user's current reward credit tally."""
    farmer_id_val = request.args.get('farmer_id')
    if farmer_id_val:
        try:
            fid = int(farmer_id_val)
        except ValueError:
            fid = farmer_id_val
        user = users_col.find_one({"farmer_id": fid})
    else:
        user = users_col.find_one({"farmer_id": DUMMY_FARMER_ID})
    
    if not user:
        return jsonify({"credit_points": 0})
    return jsonify({"credit_points": user.get("credit_points", 0)})

def get_centroid(geom):
    """Calculates the centroid of a GeoJSON geometry polygon."""
    try:
        if not geom:
            return None
        coords = geom.get('coordinates') if isinstance(geom, dict) else None
        if not coords:
            return None
        pts = coords[0] if isinstance(coords[0], list) else coords
        xs = [p[0] for p in pts if isinstance(p, list) and len(p) >= 2]
        ys = [p[1] for p in pts if isinstance(p, list) and len(p) >= 2]
        if not xs or not ys:
            return None
        return sum(xs) / len(xs), sum(ys) / len(ys)
    except Exception as e:
        print("Error getting centroid:", str(e))
        return None

def coordinates_are_close(geom1, geom2, tolerance=0.005):
    """Checks if the centroids of two geometries are within tolerance (approx 500m)."""
    c1 = get_centroid(geom1)
    c2 = get_centroid(geom2)
    if not c1 or not c2:
        return False
    return abs(c1[0] - c2[0]) < tolerance and abs(c1[1] - c2[1]) < tolerance

@app.route('/api/analyze-field', methods=['POST'])
def analyze_field():
    if not session.get('user_id'):
        return jsonify({"status": "error", "message": "Unauthorized. Please sign in or register first."}), 401
        
    try:
        is_ee_ready = ee.data.is_initialized()
    except Exception:
        is_ee_ready = False

    if not is_ee_ready:
        print("🔄 Verification fallback: Re-authenticating dynamic context request stream...")
        if not force_ee_initialization():
            return jsonify({"status": "error", "message": "Earth Engine client library is currently uninitialized on the host."}), 500

    try:
        data = request.get_json()
        if not data or 'geometry' not in data:
            return jsonify({"status": "error", "message": "Missing GeoJSON geometry"}), 400
        
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        one_month_ago = (now - timedelta(days=30)).strftime('%Y-%m-%d')

        geojson_geometry = data['geometry']
        aoi = ee.Geometry.Polygon(geojson_geometry['coordinates'])

        # Fetch Sentinel-2 composite
        s2_collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                         .filterBounds(aoi)
                         .filterDate(one_month_ago, today)
                         .sort('CLOUDY_PIXEL_PERCENTAGE')
                         .first())
        
        if s2_collection is None:
            return jsonify({"status": "error", "message": "No satellite imagery found"}), 400
            
        field_image = s2_collection.clip(aoi)

        # Calculate indices
        ndvi = field_image.normalizedDifference(['B8', 'B4']).rename('NDVI')
        ndmi = field_image.normalizedDifference(['B8', 'B11']).rename('NDMI')

        sick_mask = ndvi.lt(0.45).Or(ndmi.lt(0.1))
        sick_pixels = sick_mask.updateMask(sick_mask)

        anomaly_vectors = sick_pixels.reduceToVectors(
            geometry=aoi,
            scale=10,
            geometryType='polygon',
            labelProperty='stress_status',
            maxPixels=1e8
        )

        anomaly_geojson = anomaly_vectors.getInfo()
        new_anomaly_count = len(anomaly_geojson.get('features', []))

        # Check for previous anomalies in this field location
        previous_scan = None
        pending_scans = history_col.find({
            "farmer_id": DUMMY_FARMER_ID,
            "status": "Pending Verification"
        }, sort=[("timestamp", -1)])
        
        for scan in pending_scans:
            if coordinates_are_close(scan.get("boundary_geometry"), geojson_geometry):
                previous_scan = scan
                break

        credit_awarded = 0
        message = "Initial field baseline stored. Clear remaining crop stress areas to earn rewards."
        save_status = "Pending Verification" if new_anomaly_count > 0 else "Clean"

        if previous_scan:
            prev_timestamp_val = previous_scan["timestamp"]
            if isinstance(prev_timestamp_val, datetime):
                prev_time = prev_timestamp_val
            else:
                prev_time = datetime.fromisoformat(str(prev_timestamp_val))
                
            days_elapsed = (now - prev_time).days
            old_anomaly_features = previous_scan.get("anomaly_data", {}).get("features", [])

            if days_elapsed < 5:
                message = f"Too early to verify! Only {days_elapsed} days elapsed. Please wait at least 5 days for the next satellite pass."
                save_status = "Pending Verification"
            elif days_elapsed > 10:
                message = f"Remediation expired! It took {days_elapsed} days (Deadline was 10 days). Baseline reset."
                history_col.update_many(
                    {"farmer_id": DUMMY_FARMER_ID, "status": "Pending Verification"},
                    {"$set": {"status": "Expired"}}
                )
            else:
                if len(old_anomaly_features) > 0 and new_anomaly_count == 0:
                    credit_awarded = 50
                    users_col.update_one(
                        {"farmer_id": DUMMY_FARMER_ID},
                        {"$inc": {"credit_points": credit_awarded}}
                    )
                    history_col.update_many(
                        {"farmer_id": DUMMY_FARMER_ID, "status": "Pending Verification"},
                        {"$set": {"status": "Resolved"}}
                    )
                    message = f"Congratulations! Crop stress cleared in {days_elapsed} days. +50 Remediation Credits added."
                    save_status = "Clean"
                elif new_anomaly_count > 0:
                    message = f"Analysis running inside window ({days_elapsed} days elapsed). Found {new_anomaly_count} remaining anomalies. Keep working!"
                    save_status = "Pending Verification"
        else:
            if new_anomaly_count == 0:
                message = "Field is completely healthy! No initial remediation required."

        # Commit current tracking record to MongoDB
        history_col.insert_one({
            "farmer_id": DUMMY_FARMER_ID,
            "timestamp": now.isoformat(),
            "status": save_status,
            "boundary_geometry": geojson_geometry,
            "anomaly_data": anomaly_geojson
        })

        # Fetch fresh current credit score balance
        updated_user = users_col.find_one({"farmer_id": DUMMY_FARMER_ID})

        return jsonify({
            "status": "success",
            "message": message,
            "data": anomaly_geojson,
            "credit_points": updated_user["credit_points"],
            "awarded": credit_awarded > 0
        })
    
    except Exception as e:
        print("Error during request processing:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

# --- PAGE ROUTING SYSTEM ---

@app.route('/')
def home():
    """Renders the landing/onboarding page of the application."""
    try:
        return render_template('landing.html')
    except Exception as e:
        print("Error rendering landing.html:", str(e))
        return "Landing page template not found.", 404

@app.route('/dashboard')
def dashboard():
    """Renders the main farmer dashboard interface."""
    if not session.get('user_id'):
        return redirect(url_for('home') + "?prompt_login=true")
    try:
        return render_template('index.html')
    except Exception as e:
        print("Error rendering index.html:", str(e))
        return "Dashboard page template not found.", 404

@app.route('/marketplace')
def marketplace():
    """Renders the marketplace showing farm medicines and essentials."""
    try:
        items = list(marketplace_col.find({}, {"_id": 0}))
        user = users_col.find_one({"farmer_id": DUMMY_FARMER_ID})
        credits = user.get("credit_points", 0) if user else 0
        return render_template('marketplace.html', items=items, credits=credits)
    except Exception as e:
        print("Error rendering marketplace.html:", str(e))
        return "Marketplace page template not found.", 500

@app.route('/admin/add-item', methods=['POST'])
def add_marketplace_item():
    """Admin-only portal endpoint to register new items into MongoDB."""
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
            
        title = data.get('title')
        item_type = data.get('type')
        description = data.get('description')
        price_val = data.get('price')
        image_url = data.get('image_url')

        if not title or not item_type or not price_val:
            return jsonify({"status": "error", "message": "Missing required fields (title, type, price)"}), 400

        if item_type not in ['medicine', 'essential']:
            return jsonify({"status": "error", "message": "Type must be 'medicine' or 'essential'"}), 400

        try:
            price = float(price_val)
        except ValueError:
            return jsonify({"status": "error", "message": "Price must be a valid number"}), 400

        if not image_url or image_url.strip() == "":
            if item_type == "medicine":
                image_url = "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?auto=format&fit=crop&w=400&q=80"
            else:
                image_url = "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=400&q=80"

        new_item = {
            "id": f"{item_type[:3]}-{str(uuid.uuid4())[:8]}",
            "title": title,
            "type": item_type,
            "description": description or "",
            "price": price,
            "image_url": image_url,
            "created_at": datetime.utcnow().isoformat()
        }

        marketplace_col.insert_one(new_item)
        
        if request.is_json:
            return jsonify({"status": "success", "message": "Item added successfully!", "item": new_item})
        else:
            return redirect(url_for('marketplace'))

    except Exception as e:
        print("Error inserting marketplace item:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/insurance-claim', methods=['GET', 'POST'])
def insurance_claim():
    """Handles GET to render form, and POST to submit claims to MongoDB."""
    if request.method == 'POST':
        try:
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form

            farmer_id = data.get('farmer_id', DUMMY_FARMER_ID)
            farmer_name = data.get('farmer_name', 'anchu')
            field_details = data.get('field_details')
            loss_percentage_val = data.get('loss_percentage')
            timeline = data.get('timeline')
            damage_assessment = data.get('damage_assessment')
            area_hectares_val = data.get('area_hectares')
            crop_type = data.get('crop_type')

            if not field_details or not loss_percentage_val or not damage_assessment:
                return jsonify({"status": "error", "message": "Missing required fields"}), 400

            try:
                loss_percentage = float(loss_percentage_val)
            except ValueError:
                return jsonify({"status": "error", "message": "Loss percentage must be a number"}), 400

            try:
                area_hectares = float(area_hectares_val) if area_hectares_val else None
            except ValueError:
                area_hectares = None

            new_claim = {
                "id": f"claim-{str(uuid.uuid4())[:8]}",
                "farmer_id": int(farmer_id) if str(farmer_id).isdigit() else farmer_id,
                "farmer_name": farmer_name,
                "field_details": field_details,
                "area_hectares": area_hectares,
                "crop_type": crop_type,
                "loss_percentage": loss_percentage,
                "timeline": timeline or "",
                "damage_assessment": damage_assessment,
                "submission_date": datetime.utcnow().isoformat(),
                "status": "pending"
            }

            claims_col.insert_one(new_claim)

            if request.is_json:
                return jsonify({"status": "success", "message": "Claim submitted successfully!", "claim_id": new_claim["id"]})
            else:
                return render_template('insurance.html', success_message="Claim submitted successfully!", claim_id=new_claim["id"])

        except Exception as e:
            print("Error submitting insurance claim:", str(e))
            return jsonify({"status": "error", "message": str(e)}), 500
            
    try:
        return render_template('insurance.html')
    except Exception as e:
        print("Error rendering insurance.html:", str(e))
        return "Insurance Claims page template not found.", 404

@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.get_json()
        name = data.get('name')
        phone = data.get('phone')
        email = data.get('email')
        address = data.get('address')
        password = data.get('password')

        if not name or not phone or not email or not address or not password:
            return jsonify({"status": "error", "message": "All fields are required"}), 400

        if users_col.find_one({"email": email}):
            return jsonify({"status": "error", "message": "Email is already registered"}), 400

        last_user = users_col.find_one(sort=[("farmer_id", -1)])
        new_farmer_id = (last_user["farmer_id"] + 1) if (last_user and "farmer_id" in last_user) else 102

        user_doc = {
            "farmer_id": new_farmer_id,
            "name": name,
            "phone": phone,
            "email": email,
            "address": address,
            "password": password,
            "credit_points": 0
        }
        users_col.insert_one(user_doc)
        
        session['user_id'] = new_farmer_id
        
        user_doc.pop("password", None)
        user_doc.pop("_id", None)
        return jsonify({"status": "success", "message": "Registration successful!", "user": user_doc})
    except Exception as e:
        print("Registration error:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"status": "error", "message": "Email and password are required"}), 400

        user = users_col.find_one({"email": email, "password": password})
        if not user:
            return jsonify({"status": "error", "message": "Invalid email or password"}), 401

        user_doc = dict(user)
        user_doc.pop("password", None)
        user_doc.pop("_id", None)
        
        session['user_id'] = user['farmer_id']
        
        return jsonify({"status": "success", "message": "Login successful!", "user": user_doc})
    except Exception as e:
        print("Login error:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user_id', None)
    return jsonify({"status": "success", "message": "Logged out successfully!"})

@app.route('/api/purchase', methods=['POST'])
def api_purchase():
    try:
        data = request.get_json()
        name = data.get('name')
        location = data.get('location')
        phone = data.get('phone')
        item_title = data.get('item_title')
        item_price_val = data.get('item_price')

        if not name or not location or not phone or not item_title:
            return jsonify({"status": "error", "message": "Buyer details are required"}), 400

        try:
            item_price = float(item_price_val)
        except ValueError:
            item_price = 0.0

        purchase_doc = {
            "id": f"order-{str(uuid.uuid4())[:8]}",
            "name": name,
            "location": location,
            "phone": phone,
            "item_title": item_title,
            "item_price": item_price,
            "timestamp": datetime.utcnow().isoformat()
        }
        orders_col.insert_one(purchase_doc)
        return jsonify({"status": "success", "message": "Order processed successfully!", "order_id": purchase_doc["id"]})
    except Exception as e:
        print("Purchase error:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/update-credits', methods=['POST'])
def api_update_credits():
    try:
        data = request.get_json()
        farmer_id = data.get('farmer_id')
        credit_points = data.get('credit_points')

        if farmer_id is None or credit_points is None:
            return jsonify({"status": "error", "message": "farmer_id and credit_points are required"}), 400

        try:
            fid = int(farmer_id)
        except ValueError:
            fid = farmer_id

        users_col.update_one(
            {"farmer_id": fid},
            {"$set": {"credit_points": int(credit_points)}}
        )
        return jsonify({"status": "success", "message": "Credits updated successfully!"})
    except Exception as e:
        print("Update credits error:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
