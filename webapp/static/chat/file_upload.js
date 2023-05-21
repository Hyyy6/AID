// function setRoute(path) {
//     route = path
// }

document.addEventListener('DOMContentLoaded', function() {
    // Open the editor
    document.getElementById('openEditor').addEventListener('click', function() {
        document.getElementById('editorContainer').style.display = 'block';
    });

    // Save the file
    document.getElementById('saveFile').addEventListener('click', function() {
        var fileContent = document.getElementById('editor').value;
        console.log(fileContent)
        formdata = new FormData()
        formdata.append('file', fileContent)
        // Make an HTTP request to save the file on the server
        var xhr = new XMLHttpRequest();
        xhr.open('POST', getRoute(this) + "/rules/set");
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    alert('File saved successfully!');
                } else {
                    alert('Failed to save the file.');
                }
            }
        };
        xhr.send(formdata);
    });

    // View the file
    document.getElementById('viewFile').addEventListener('click', function() {
        // Fetch the file from the server using an HTTP request
        var xhr = new XMLHttpRequest();
        xhr.open('GET', getRoute(this) + "/rules/get");
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    document.getElementById('fileContent').textContent = xhr.responseText;
                    document.getElementById('fileContents').style.display = 'block';
                    document.getElementById('uploadFile').style.display = 'block';
                } else {
                    alert('Failed to fetch the file.');
                }
            }
        };
        xhr.send();
    });

    // Upload the file
    document.getElementById('upload').addEventListener('click', function() {
        var file = document.getElementById('fileInput').files[0];
        var formData = new FormData();
        formData.append('file', file);

        // Make an HTTP request to upload the file to the server
        var xhr = new XMLHttpRequest();
        xhr.open('POST', getRoute(this) + "/roules/set");
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    alert('File uploaded successfully!');
                } else {
                    alert('Failed to upload the file.');
                }
            }
        };
        xhr.send(formData);
    });
});
