document.addEventListener('DOMContentLoaded', () => {

    const generateButton = document.getElementById('generate-button');
    const sectorInput = document.getElementById('sector-input');
    const themeInput = document.getElementById('theme-input');
    // IMPORTANT: Mise à jour de l'ID du conteneur de résultats
    const resultsContainer = document.getElementById('results-container');
    const loader = document.getElementById('loader');

    // Cacher le loader au démarrage
    loader.style.display = 'none';

    generateButton.addEventListener('click', async () => {
        const sector = sectorInput.value;
        const theme = themeInput.value;

        if (!sector) {
            alert("Veuillez renseigner votre secteur d'activité.");
            return;
        }

        // Afficher le loader et vider les anciens résultats
        loader.style.display = 'block';
        resultsContainer.innerHTML = '';

        try {
            const response = await fetch('/generate-spark', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ sector: sector, theme: theme }),
            });

            loader.style.display = 'none';

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Erreur du serveur: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.ideas && data.ideas.length > 0) {
                // Utiliser la nouvelle fonction pour afficher les cartes
                displayIdeas(data.ideas);
            } else {
                resultsContainer.innerHTML = `<p class="error">Aucune idée n'a pu être générée. Essayez une autre requête.</p>`;
            }

        } catch (error) {
            console.error("Erreur lors de l'appel fetch:", error);
            loader.style.display = 'none';
            resultsContainer.innerHTML = `<p class="error">Oups, une erreur est survenue : ${error.message}</p>`;
        }
    });

    // NOUVELLE FONCTION POUR AFFICHER LES CARTES
    function displayIdeas(ideas) {
        resultsContainer.innerHTML = ''; // On vide au cas où
        ideas.forEach((idea, index) => {
            const card = document.createElement('div');
            card.className = 'result-card';
            // Ajoute un délai à l'animation pour un effet d'escalier
            card.style.animationDelay = `${index * 0.1}s`;

            // Choisir une icône simple pour le format
            let formatIcon = '✍️'; // Post Texte
            if (idea.format.toLowerCase().includes('reel')) formatIcon = '🎬';
            if (idea.format.toLowerCase().includes('carrousel')) formatIcon = '🖼️';
            if (idea.format.toLowerCase().includes('story')) formatIcon = '⚡️';
            if (idea.format.toLowerCase().includes('image')) formatIcon = '📷';

            card.innerHTML = `
                <div class="card-header">
                    <span class="format-icon">${formatIcon}</span>
                    <span>${idea.format}</span>
                </div>
                <h3>${idea.titre}</h3>
                <p class="description">${idea.description}</p>
                <div class="pro-tip">
                    <strong>Pro Tip:</strong> ${idea.pro_tip}
                </div>
            `;
            resultsContainer.appendChild(card);
        });
    }
});