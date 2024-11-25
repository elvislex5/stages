document.getElementById('search-input').addEventListener('input', function(event) {
    event.preventDefault(); // Empêcher le rechargement de la page
    let query = this.value;

    if (query.length > 0) {
        fetch(`/offres/search/?q=${query}`)
            .then(response => response.json())
            .then(data => {
                let resultsContainer = document.getElementById('search-results');
                resultsContainer.innerHTML = '';  // Réinitialiser le contenu de la div

                if (data.results && data.results.length > 0) {
                    data.results.forEach(result => {
                        let resultItem = document.createElement('div');
                        resultItem.innerHTML = `<p>${result.titre}</p><p>${result.description}</p>`;
                        resultsContainer.appendChild(resultItem);
                    });
                } else {
                    resultsContainer.innerHTML = '<p>Aucun résultat trouvé</p>';
                }
            })
            .catch(error => {
                console.error('Erreur lors de la recherche:', error);
            });
    } else {
        document.getElementById('search-results').innerHTML = ''; // Effacer la div si le champ est vide
    }
});
