const formatContainer = document.getElementById('format-container');
const dataContainer = document.getElementById('data-container');
console.log(dataContainer.innerText);

// Parse JSON data
let reportData = JSON.parse(formatContainer.innerText);
let tableData = JSON.parse(dataContainer.innerText);
console.log(tableData);

// Function to extract values from object
function getValuesFromObject(Data) {
    return Object.values(Data);
}

console.log(getValuesFromObject(tableData)); // Output: ["Alice", 30, "Wonderland", "Explorer"]

// Function to create group button with toggle functionality
function createGroupButton(group, columnIndices) {
    const button = document.createElement('a');
    button.className = 'btn-small waves-effect waves-light button collapse-button';
    button.style.backgroundColor = group.group_color;
    button.innerHTML = `<i class="material-icons">${group.group_icon}</i><span>${group.group_title}</span>`;
    button.title = group.group_title;
    button.dataset.collapsed = "false";

    button.addEventListener('mousedown', (e) => e.preventDefault());

    button.addEventListener('click', function () {
        const currentHiddenColumns = hot.getSettings().hiddenColumns.columns || [];
        const allColumnsVisible = columnIndices.every(index => !currentHiddenColumns.includes(index));
        const newHiddenColumns = allColumnsVisible
            ? [...currentHiddenColumns, ...columnIndices]
            : currentHiddenColumns.filter(index => !columnIndices.includes(index));

        hot.updateSettings({
            hiddenColumns: {
                columns: newHiddenColumns,
                indicators: true
            }
        });

        button.classList.toggle('collapsed', allColumnsVisible);
    });

    return button;
}

// Function to build table from JSON data
function buildTableFromJson(reportData) {
    const fieldGroups = reportData.field_groups;
    const nestedHeaders = [];
    const columns = [];
    const buttonContainer = document.getElementById('dynamic-buttons');

    // Clear previous buttons if any
    buttonContainer.innerHTML = '';

    const columnIndicesPerGroup = [];  // Track column indices for each group

    const groupHeaders = [];
    const individualHeaders = [];

    fieldGroups.forEach((group) => {
        const columnIndices = [];

        group.fields.forEach(field => {
            individualHeaders.push(field.field_label);
            columns.push({
                data: field.field_name,
                type: field.field_type === 'number' ? 'numeric' : 'text'
            });
            columnIndices.push(columns.length - 1);
        });

        columnIndicesPerGroup.push(columnIndices);

        const button = createGroupButton(group, columnIndices);
        buttonContainer.appendChild(button);

        groupHeaders.push({ label: group.group_title, colspan: group.fields.length });
    });

    nestedHeaders.push(groupHeaders, individualHeaders);

    return { nestedHeaders, columns };
}

let hot;  // Global Handsontable instance

// Initialize Handsontable
function initializeHandsontable(reportData, tableData) {
    const tableSettings = buildTableFromJson(reportData);
    const container = document.getElementById("spreadsheet");


    if (tableData.length === 0) {
        const defaultRow = tableSettings.columns.map(() => null); // Create a blank row with `null` values
        tableData.push(defaultRow);
    }

    hot = new Handsontable(container, {
        data: tableData,
        colHeaders: true,
        rowHeaders: true,
        autoColumnSize: false,
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
        licenseKey: 'non-commercial-and-evaluation',
        afterChange: function (changes, source) {
            if (source === 'edit') ensureEmptyRow();
        }
    });

    const applyGroupColorStyling = (headers, col, callback) => {
        let startColIndex = 0;
        for (let i = 0; i < headers.length; i++) {
            if (col >= startColIndex && col < startColIndex + headers[i].colspan) {
                callback(i);
                break;
            }
            startColIndex += headers[i].colspan;
        }
    };

    hot.updateSettings({
        afterGetColHeader: (col, TH) => applyGroupColorStyling(tableSettings.nestedHeaders[0], col, (i) => {
            TH.style.backgroundColor = reportData.field_groups[i].group_color;
        }),
        afterRenderer: (TD, row, col) => applyGroupColorStyling(tableSettings.nestedHeaders[0], col, (i) => {
            TD.style.backgroundColor = reportData.field_groups[i].group_color;
        })
    });
}

// Ensure the last row is empty
function ensureEmptyRow() {
    if (!isLastRowEmpty()) {
        hot.alter('insert_row');
    }
}

// Check if the last row is empty
function isLastRowEmpty() {
    const lastRowData = hot.getDataAtRow(hot.countRows() - 1);
    return lastRowData.every(cell => cell === null || cell === '');
}

// Initialize Handsontable and check the last row on load
initializeHandsontable(reportData, tableData);
ensureEmptyRow();

// Handle form submission
document.querySelector('button[type="submit"]').addEventListener('click', function (event) {
    event.preventDefault();
    handleSubmit();
});

function handleSubmit() {
    const tableData = hot.getData();
    const columnNames = hot.getSettings().columns.map(col => col.data);

    const formattedData = tableData.map(row => {
        return columnNames.reduce((rowObject, colName, index) => {
            rowObject[colName] = row[index];
            return rowObject;
        }, {});
    });

    sendJsonData(JSON.stringify({ table_data: formattedData }));
}

// Send JSON data to the backend
function sendJsonData(jsonData) {
    fetch('/submitTable', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: jsonData
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {
        console.log('Success:', data);
        M.toast({html: 'successfully submitted!', classes: 'green'});
    })
    .catch((error) => {
        console.error('Error:', error);
        M.toast({html: 'Error', classes: 'red'});
    });
}

document.getElementById('export').addEventListener('click', function () {
    // Get Handsontable data
    const tableData = hot.getData();

    // Get the nested headers (group headers and subheaders)
    const nestedHeaders = hot.getSettings().nestedHeaders;

    // Initialize the export data array
    const exportData = [];

    // If there are nested headers, we need to process them
    if (nestedHeaders && nestedHeaders.length > 0) {
        // Process the first row of nested headers (group headers)
        const groupHeaderRow = [];
        nestedHeaders[0].forEach(header => {
            if (typeof header === 'object') {
                // Add the group label to the start of its span
                groupHeaderRow.push(header.label);
                // Add empty cells for the rest of the colspan
                for (let i = 1; i < header.colspan; i++) {
                    groupHeaderRow.push(null); // Empty cells to maintain alignment
                }
            } else {
                groupHeaderRow.push(header); // Just a string header (unlikely for group headers)
            }
        });
        exportData.push(groupHeaderRow); // Add the properly aligned group headers
    }

    // Process the second row of nested headers (subheaders)
    if (nestedHeaders && nestedHeaders.length > 1) {
        exportData.push(nestedHeaders[1]);
    }

    // Add table data below the headers
    exportData.push(...tableData);

    // Convert the data to a worksheet format
    const worksheet = XLSX.utils.aoa_to_sheet(exportData);

    // Handle merged cells for group headers
    const merges = [];
    let startColIndex = 0;

    if (nestedHeaders && nestedHeaders.length > 0) {
        nestedHeaders[0].forEach((header, index) => {
            if (typeof header === 'object' && header.colspan > 1) {
                // Define the merge range for the group header
                merges.push({
                    s: { r: 0, c: startColIndex }, // Start cell for merge
                    e: { r: 0, c: startColIndex + header.colspan - 1 } // End cell for merge
                });
            }
            startColIndex += (header.colspan || 1); // Increment by colspan or 1
        });
    }

    worksheet['!merges'] = merges;

    // Set column widths based on Handsontable's column widths
    const colWidths = [];
    for (let i = 0; i < hot.countCols(); i++) {
        colWidths.push({ wpx: hot.getColWidth(i)*.75 || 100 }); // Default to 100px if no width is set
    }
    worksheet['!cols'] = colWidths;

    // Create a new workbook
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Table Data');

    // Export the workbook to an Excel file
    XLSX.writeFile(workbook, 'handsontable_data.xlsx');
});
