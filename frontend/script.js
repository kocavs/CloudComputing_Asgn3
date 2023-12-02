var apigClient = apigClientFactory.newClient();

document.getElementById('search-button').addEventListener('click', function() {
    const query = document.getElementById('search-query').value;
    // Use the SDK's searchGet method
    apigClient.searchGet({ q: query }, null, {})
        .then(function(response) {
            // Success - Display the results
            console.log(response)
            displaySearchResults(response.data.results);
        }).catch(function(error) {
            // Handle the error
            console.error(error);
        });
});

function displaySearchResults(results) {

    const resultsContainer = document.getElementById('search-results');
    resultsContainer.innerHTML = ''; // Clear previous results
    results.forEach(photo => {
        const imgElement = document.createElement('img');
        imgElement.src = photo.url;
        resultsContainer.appendChild(imgElement);
    });
}

document.getElementById('upload-button').addEventListener('click', function() {
    const files = document.getElementById('photo-upload').files;
    const customLabelsInput = document.getElementById('custom-labels').value;

    if (!customLabelsInput) {
        console.error('Custom labels must be defined');
        return;
    }

    // Split and trim custom labels
    const customLabels = customLabelsInput.split(',')
                                          .map(label => label.trim())
                                          .join(',');

    Array.from(files).forEach(file => {

        let params = {
            'bucket': 'b2photocollection', // Adjust as needed
            'key': file.name, // File name as the key
            'x-amz-meta-customLabels': customLabels
        };

        let additionalParams = {
            headers: {
                'Content-Type': file.type
            }
        };

        let bodyData = {
            fileData: file
        };

        // Make the API call
        apigClient.uploadPut(params, bodyData, additionalParams)
            .then(function(response) {
                console.log('File uploaded successfully.');
            }).catch(function(error) {
                console.error('Upload error:', error);
            });
    });
});



