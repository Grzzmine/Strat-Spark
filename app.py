from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import openai
import os
import json


load_dotenv()


app = Flask(__name__)


api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("La clé API OpenAI n'est pas définie. Vérifiez votre fichier .env")
client = openai.OpenAI(api_key=api_key)

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/generate-spark', methods=['POST'])
def generate_spark():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Requête invalide, pas de JSON reçu."}), 400

    user_sector = data.get('sector')
    user_theme = data.get('theme')

    if not user_sector:
        return jsonify({"error": "Le secteur d'activité est obligatoire."}), 400

    try:
        base_prompt_instruction = """
        Tu es Strat'Spark, un expert en stratégie de contenu pour TPE et indépendants.
        Génère 10 idées de contenu créatives et engageantes. Pour chaque idée, fournis :
        1. Un titre accrocheur ("titre").
        2. Le format idéal ("format") parmi : "Reel", "Carrousel", "Story", "Post Image", "Post Texte".
        3. Une description détaillée et concrète ("description").
        4. Un "pro_tip" pour maximiser l'impact.
        
        Varie les formats et les angles d'approche.
        La réponse DOIT être un objet JSON valide avec une clé "ideas" contenant une liste de 10 objets.
        """

        if user_theme:
            final_prompt = f"""
            {base_prompt_instruction}
            Le secteur d'activité est : "{user_sector}".
            Toutes les idées doivent OBLIGATOIREMENT se concentrer sur le thème suivant : "{user_theme}".
            """
        else:
            final_prompt = f"""
            {base_prompt_instruction}
            Le secteur d'activité est : "{user_sector}".
            Génère des idées générales et variées pour ce secteur.
            """

        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Tu es un assistant de création de contenu spécialisé pour les TPE. Tu réponds uniquement en format JSON valide."},
                {"role": "user", "content": final_prompt}
            ]
        )
        
        content_ideas = json.loads(response.choices[0].message.content)
        
       
        return jsonify(content_ideas)

    except openai.APIConnectionError as e:
        print(f"Erreur de connexion à l'API OpenAI: {e}")
        return jsonify({"error": "Impossible de se connecter aux serveurs d'OpenAI. Veuillez réessayer plus tard."}), 503
    except openai.RateLimitError as e:
        print(f"Erreur de limite de taux: {e}")
        return jsonify({"error": "Trop de requêtes ont été envoyées. Veuillez attendre un moment."}), 429
    except openai.APIStatusError as e:
        print(f"Erreur de statut de l'API OpenAI: {e.status_code} - {e.response}")
        return jsonify({"error": f"Une erreur est survenue du côté d'OpenAI (Code: {e.status_code})."}), 500
    except Exception as e:
        
        print(f"Une erreur imprévue est survenue: {e}")
        return jsonify({"error": "Désolé, une erreur interne est survenue. L'équipe technique a été notifiée."}), 500