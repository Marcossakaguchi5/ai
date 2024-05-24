from flask import Flask, request, render_template, redirect, url_for
import os
import logging
from PIL import Image
from ultralytics import YOLO

# Initialize the Flask app
app = Flask(__name__)

# Configure upload directory
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Load the YOLOv8 model
try:
    model = YOLO('besty.pt')  # Corrigido o nome do arquivo
    logging.info("Model loaded successfully.")
except Exception as e:
    logging.error(f"Error loading model: {e}")
    model = None

# Function to predict the class of an image
def predict(image_path):
    try:
        img = Image.open(image_path)
        results = model(img)  # Executa a inferência
        
        predictions = []
        for result in results:  # Itera sobre os resultados
            for detection in result.boxes.data.tolist():
                class_id = int(detection[5])
                prediction = {
                    'class': model.names[class_id],  # Nome da classe
                    'confidence': detection[4],  # Confiança da predição
                    'box': detection[:4]  # Coordenadas da caixa delimitadora
                }
                predictions.append(prediction)
        
        logging.debug(f"Predictions: {predictions}")
        return predictions
    except Exception as e:
        logging.error(f"Error during prediction: {e}")
        return None

# Route for image upload
@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            predictions = predict(filename)
            if predictions:
                return render_template('result.html', predictions=predictions)
            else:
                return "An error occurred during prediction. Please try again."
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
