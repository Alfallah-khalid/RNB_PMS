const dataContainer = document.getElementById('data-container');
console.log(dataContainer.innerText);
console.log(dataContainer.innerText.length);
// Parse jasonData as JSON since it's coming as a string
let jasonData = JSON.parse(dataContainer.innerText );
console.log(jasonData);



function buildTableFromJson(reportData) {
    const fieldGroups = reportData.field_groups;
    const nestedHeaders = [];
    const columns = [];
    const buttonContainer = document.getElementById('dynamic-buttons');
    
    // Clear previous buttons if any
    buttonContainer.innerHTML = '';

    const columnIndicesPerGroup = [];  // To track column indices for each group

    // Prepare the first row of nested headers (group headers)
    const groupHeaders = [];
    const individualHeaders = [];

    // Loop through each group and field
    fieldGroups.forEach((group, groupIndex) => {
        const groupTitle = group.group_title;
        const groupColor = group.group_color;
        const groupIcon = group.group_icon;
        const columnIndices = []; // To track indices for this group

        // Create buttons for each group to toggle visibility
        const button = document.createElement('a');
        button.className = 'btn-small waves-effect waves-light button collapse-button';
        button.style.backgroundColor = groupColor; // Keep background color here, no CSP restrictions
        button.innerHTML = `<i class="material-icons">${groupIcon}</i><span>${groupTitle}</span>`;
        button.title = groupTitle;  // Tooltip showing the label
        button.dataset.collapsed = "false"; // Track collapsed state with a data attribute
        buttonContainer.appendChild(button);

        // Prevent text selection on button click
        button.addEventListener('mousedown', function (e) {
            e.preventDefault();
        });

        // Prepare group header
        groupHeaders.push({ label: groupTitle, colspan: group.fields.length });

        // Prepare individual headers and column settings
        group.fields.forEach((field) => {
            individualHeaders.push(field.field_label);

            // Determine the field type and set appropriate Handsontable column config
            let columnConfig = {
                data: field.field_name,
                type: field.field_type === 'number' ? 'numeric' : 'text'
            };
            columns.push(columnConfig);

            // Track column index for this group
            columnIndices.push(columns.length - 1); // Store the current column index
        });

        // Store column indices for toggling
        columnIndicesPerGroup.push(columnIndices);

        // Add event listener to the button for hiding/showing this group's columns
        button.addEventListener('click', function () {
            const currentHiddenColumns = hot.getSettings().hiddenColumns.columns || [];
            const allColumnsVisible = columnIndices.every(index => !currentHiddenColumns.includes(index));
            const newHiddenColumns = allColumnsVisible
                ? [...currentHiddenColumns, ...columnIndices]
                : currentHiddenColumns.filter(index => !columnIndices.includes(index));

            // Update Handsontable to hide or show the columns
            hot.updateSettings({
                hiddenColumns: {
                    columns: newHiddenColumns,
                    indicators: true
                }
            });

            // Toggle the button state: Add or remove "collapsed" class
            if (allColumnsVisible) {
                button.classList.add('collapsed');  // Add class to show the label
            } else {
                button.classList.remove('collapsed');  // Remove class to hide the label
            }
        });
    });

    // Add headers for Handsontable configuration
    nestedHeaders.push(groupHeaders);
    nestedHeaders.push(individualHeaders);

    return { nestedHeaders, columns };
}

let hot;  // Declare hot globally to access it inside functions

// Function to initialize Handsontable
function initializeHandsontable(reportData) {
    const tableSettings = buildTableFromJson(reportData);

    const container = document.getElementById("spreadsheet");
    
    hot = new Handsontable(container, {
        data: Array.from({ length: 5 }, () => ({})),  // Create 5 unique empty rows
        colHeaders: true,
        rowHeaders: true,
        height: 450,
        nestedHeaders: tableSettings.nestedHeaders,
        columns: tableSettings.columns,
        hiddenColumns: {
            columns: [],
            indicators: true
        },
        contextMenu: true,
        dropdownMenu: true,
        manualColumnResize: true,
        copyable: true,  // Ensure copyable option is enabled
        licenseKey: 'non-commercial-and-evaluation' // Free version of Handsontable
    });

    // Apply custom colors for the headers dynamically based on group_color
    hot.updateSettings({
        afterGetColHeader: function (col, TH) {
            const groupHeader = tableSettings.nestedHeaders[0];
            let startColIndex = 0;
            for (let i = 0; i < groupHeader.length; i++) {
                const group = groupHeader[i];
                if (col >= startColIndex && col < startColIndex + group.colspan) {
                    TH.style.backgroundColor = reportData.field_groups[i].group_color;
                    break;
                }
                startColIndex += group.colspan;
            }
        },

        // Apply row colors dynamically
        afterRenderer: function (TD, row, col) {
            const groupHeader = tableSettings.nestedHeaders[0];
            let startColIndex = 0;

            for (let i = 0; i < groupHeader.length; i++) {
                const group = groupHeader[i];
                if (col >= startColIndex && col < startColIndex + group.colspan) {
                    TD.style.backgroundColor = reportData.field_groups[i].group_color;
                    break;
                }
                startColIndex += group.colspan;
            }
        }
    });

    // Handle custom copy with headers and group headers
    hot.updateSettings({
        beforeCopy: function (data, coords) {
            // Add group headers and column headers to the copied data
            const headersRow = [tableSettings.nestedHeaders[1]]; // Add column headers (individualHeaders)
            const groupHeadersRow = [tableSettings.nestedHeaders[0].map(g => g.label)]; // Add group headers (groupHeaders)
            
            // Prepend headers to copied data
            data.unshift(headersRow);
            data.unshift(groupHeadersRow);
        }
    });
}




  initializeHandsontable(jasonData);
  