// base URL
var apiBaseUrl = 'http://localhost:8012';

// convert form data to a query string
function formDataToQueryString(formData) {
    var params = '';
    for (var pair of formData.entries()) {
        if (pair[1]) {
            params += pair[0] + '=' + encodeURIComponent(pair[1]) + '&';
        }
    }
    return params.slice(0, -1); // remove the last '&'
}

// filter users
document.getElementById('filterUsersForm').onsubmit = function(event) {
    event.preventDefault();
    var formData = new FormData(event.target);
    getUsers(formData);
};

// get all users
document.getElementById('getAllUsersButton').onclick = function() {
    getUsers();
};

// get users (for filter users & get all users)
function getUsers(formData = null) {
    var url = apiBaseUrl + '/users';
    if (formData) {
        url += '?' + formDataToQueryString(formData);
    }
    fetch(url)
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            var resultContainer = document.getElementById('getUsersResult');
            resultContainer.innerHTML = '';
            if (Array.isArray(data) && data.length > 0) {
                data.forEach(function(user) {
                    var userString = 'ID: ' + user.id + ', Username: ' + user.username + ', Name: ' + user.first_name + ' ' + user.last_name + ', Email: ' + user.email + ', Credit: ' + user.credit + ', OpenID: ' + user.openid + ', Role: ' + user.role;
                    var userDiv = document.createElement('div');
                    userDiv.textContent = userString;
                    resultContainer.appendChild(userDiv);
                });
            } else {
                resultContainer.textContent = 'No (such) users were found';
            }
        })
        .catch(function(error) {
            console.error('Error:', error);
        });
}

// create a user (POST)
document.getElementById('createUserForm').onsubmit = function(event) {
    event.preventDefault();
    var formData = new FormData(event.target);
    var userData = {};
    formData.forEach(function(value, key) {
        userData[key] = value;
    });

    fetch(apiBaseUrl + '/users', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        alert('User created');
    })
    .catch(function(error) {
        alert('Error creating user');
        console.error('Error:', error);
    });
};

// update a user (PUT)
document.getElementById('updateUserForm').onsubmit = function(event) {
    event.preventDefault();
    var formData = new FormData(event.target);
    // find matching user
    var userId = formData.get('id');
    formData.delete('id');

    var userData = {};
    // update each filled field
    formData.forEach(function(value, key) {
        if (value) userData[key] = value;
    });

    fetch(apiBaseUrl + '/users/' + userId, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        alert('User updated');
    })
    .catch(function(error) {
        alert('Error updating user');
        console.error('Error:', error);
    });
};

// delete a user (DELETE)
document.getElementById('deleteUserForm').onsubmit = function(event) {
    event.preventDefault();
    var userId = document.getElementById('deleteUserId').value;
    fetch(apiBaseUrl + '/users/' + userId, {
        method: 'DELETE',
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        alert('User deleted');
    })
    .catch(function(error) {
        alert('Error deleting user');
        console.error('Error:', error);
    });
};