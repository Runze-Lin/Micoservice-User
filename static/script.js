const apiBaseUrl = 'http://localhost:8012'; // Base URL for the API

// Function to get users
function getUsers() {
    fetch(`${apiBaseUrl}/users`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('getUsersResult').innerHTML = JSON.stringify(data, null, 2);
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// Function to create a user
document.getElementById('createUserForm').addEventListener('submit', function(event) {
    event.preventDefault();
    let formData = new FormData(event.target);
    let userData = Object.fromEntries(formData.entries());
    fetch(`${apiBaseUrl}/users`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
    })
    .then(response => response.json())
    .then(data => {
        alert('User created');
        // Optionally, clear the form or provide further user feedback
    })
    .catch(error => {
        alert('Error creating user');
        console.error('Error:', error);
    });
});

// Function to update a user
document.getElementById('updateUserForm').addEventListener('submit', function(event) {
    event.preventDefault();
    let formData = new FormData(event.target);
    let userId = formData.get('id'); // Extract the user ID to use in the URL
    formData.delete('id'); // Remove ID from formData since it's not needed in the request body

    let userData = {};
    formData.forEach((value, key) => {
        if (value) userData[key] = value; // Only add fields that have values
    });

    fetch(`${apiBaseUrl}/users/${userId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
    })
    .then(response => response.json())
    .then(data => {
        alert('User updated');
        // Optionally, clear the form or provide further user feedback
    })
    .catch(error => {
        alert('Error updating user');
        console.error('Error:', error);
    });
});

// Function to delete a user
function deleteUser() {
    let userId = document.getElementById('deleteUserId').value;
    fetch(`${apiBaseUrl}/users/${userId}`, {
        method: 'DELETE',
    })
    .then(response => response.json())
    .then(data => {
        alert('User deleted');
        // Optionally, clear the input field or provide further user feedback
    })
    .catch(error => {
        alert('Error deleting user');
        console.error('Error:', error);
    });
}
