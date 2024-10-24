var elem = document.querySelector('.massr');
var msnry = new Masonry( elem, {
  // options
  itemSelector: '.grid-item',
  columnWidth: 200,
  gutter: 10
  
});

// Get the data container and parse JSON data
const dataContainer = document.getElementById('data-container');
let jasonData = JSON.parse(dataContainer.innerText);  // Parse JSON data

// Function to build the dynamic div-based structure from the JSON data
function buildDivsFromJson(reportData) {
    const fieldGroups = reportData.field_groups;
    const container = document.getElementById('form-container'); // This is where the groups will be placed

    // Clear previous content if any
    container.innerHTML = '';

    // Loop through each field group
    fieldGroups.forEach(group => {
        // Create a div for the group container
        const groupDiv = document.createElement('div');
        groupDiv.className = 'group-container col m6';  // Add a class for styling the group

        // Create the group header
        const groupHeader = document.createElement('div');
        groupHeader.className = 'group-header';  // Class for styling the header
        groupHeader.style.backgroundColor = group.group_color;  // Apply group color
        groupHeader.innerHTML = `<i class="material-icons">${group.group_icon}</i><span>${group.group_title}</span>`;
        
        // Append the header to the group container
        groupDiv.appendChild(groupHeader);

        // Create a div for the fields
        const fieldsDiv = document.createElement('div');
        fieldsDiv.className = 'fields-container';  // Class for styling the fields container

        // Loop through each field in the group
        group.fields.forEach(field => {
            // Create a div for each field
            const fieldDiv = document.createElement('div');
            fieldDiv.className = 'field-container';  // Class for styling the individual field

            // Create label for the field
            const label = document.createElement('label');
            label.innerText = field.field_label;
            label.className = 'field-label';  // Class for field label

            // Create input based on field type
            let input;
            if (field.field_type === 'number') {
                input = document.createElement('input');
                input.type = 'number';
            } else {
                input = document.createElement('input');
                input.type = 'text';
            }
            input.className = 'field-input';  // Add class for styling inputs
            input.name = field.field_name;

            // Append label and input to the field div
            fieldDiv.appendChild(label);
            fieldDiv.appendChild(input);

            // Append the field div to the fields container
            fieldsDiv.appendChild(fieldDiv);
        });

        // Append the fields container to the group container
        groupDiv.appendChild(fieldsDiv);

        // Append the group container to the main form container
        container.appendChild(groupDiv);
        container.style.height = 'auto'; // Reset any fixed height
    });
}

// Initialize the dynamic div-based HTML structure
buildDivsFromJson(formatData);


window.onresize = function() {
    const container = document.getElementById('form-container'); // This is where the groups will be placed
    //container.style.height = 'auto'; // Reset any fixed height
};









// Get the submit button
const submitButton = document.querySelector('button[type="submit"]');

// Event listener for form submission
submitButton.addEventListener('click', function(event) {
    event.preventDefault(); // Prevent the default form submission
    handleSubmit();
});

// Function to handle the form submission
function handleSubmit() {
    // Collect form data
    const formData = {};
    const fieldInputs = document.querySelectorAll('.field-input');
    fieldInputs.forEach(input => {
        formData[input.name] = input.value;
    });

    // Add metadata


    // Convert to JSON
    const jsonData = JSON.stringify(formData);

    // Send JSON data to the server
    sendJsonData(jsonData);
}

// Function to send JSON data to the server
function sendJsonData(jsonData) {
    fetch('/submitForm', {  // Replace '/your-endpoint-url' with your actual backend endpoint
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: jsonData
    })
    .then(response => response.json())
    .then(data => {
        data
        console.log('Success:', data);
        // You can add code here to handle a successful submission, like showing a success message
    })
    .catch((error) => {
        console.error('Error:', error);
        // Handle error case
    });
}

