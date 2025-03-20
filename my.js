const baseUrl = "http://127.0.0.1:5000";

// Ensure event listener is added once the DOM is fully loaded
document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("uploadBtn").addEventListener("click", uploadFile);
   
});
// document.getElementById("datatye").addEventListener("change", function () {
//     let selecteddatatype = this.value;
//     sessionStorage.setItem("selecteddata", selecteddatatype);
//     console.log("Stored selectedColumn2:", selectedValue);
// });
// Upload CSV and Fetch EDA results
async function uploadFile() {
    
    let fileInput = document.getElementById("csvFile");
    if (!fileInput.files.length) {
        console.error("No file selected.");
        return;
    }

    let formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
        let response = await fetch("http://127.0.0.1:5000/upload", {
            method: "POST",
            body: formData
        });

        let result = await response.json();
        console.log("result", result);
        if (!response.ok) {
            throw new Error(result.error || "Unknown error");
        }
        document.getElementById("summaryStats").textContent = JSON.stringify(result.summary, null, 2);
        document.getElementById("missingValues").textContent = JSON.stringify(result.missing_values, null, 2);
        document.getElementById("columns").textContent = JSON.stringify(result.columns, null, 2);
        sessionStorage.setItem("columns", JSON.stringify(result.columns));
        document.getElementById("shape").textContent = JSON.stringify(result.shape, null, 2);
        console.log("File uploaded successfully:", result);
        
        let columns = JSON.parse(sessionStorage.getItem("columns"));
        dropdown("selectc1", columns);
        dropdown("selectc2", columns);
    } catch (error) {
        console.error("Error uploading file:", error);
    }
}
function dropdown(id,columns) {
    let dropdown = document.getElementById(id);
    dropdown.innerHTML = '<option value="">Select</option>';  // Reset previous options

    columns.forEach(option => {
        let newOption = document.createElement("option");
        newOption.value = option;
        newOption.textContent = option;
        dropdown.appendChild(newOption);
    });
}
// Listen to dropdown changes and store selected values
document.getElementById("selectc1").addEventListener("change", function () {
    let selectedValue = this.value;
    sessionStorage.setItem("selectedColumn1", selectedValue);
    console.log("Stored selectedColumn1:", selectedValue);
    let columns = JSON.parse(sessionStorage.getItem("columns"));
    let selectedColumn1 = sessionStorage.getItem("selectedColumn1");
    let filteredColumns = columns.filter(column => column !== selectedColumn1);
    dropdown("selectc2", filteredColumns);
});
document.getElementById("selectc2").addEventListener("change", function () {
    let selectedValue = this.value;
    sessionStorage.setItem("selectedColumn2", selectedValue);
    console.log("Stored selectedColumn2:", selectedValue);
});
async function EDA() {
    x= sessionStorage.getItem("selectedColumn1");
    y= sessionStorage.getItem("selectedColumn2");
    console.log(x);
    console.log(y);
    body={
        "x":x,
        "y":y
    }
    try {
        let response = await fetch("http://127.0.0.1:5000/eda", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(body),
        });
        let result = await response.json();
        console.log("result", result);
        if (!response.ok) {
            throw new Error(result.error || "Unknown error");
        }
        sessionStorage.setItem("result", JSON.stringify(result));
        document.getElementById("histogramImg").src = result.histogram;
        document.getElementById("bargraphImg").src = result.barchart;
        document.getElementById("piechartimg").src = result.piechart;
        document.getElementById("heatmapImg").src = result.heatmap;
        document.getElementById("pairplotImg").src = result.pairplot;
        document.getElementById("violinplotImg").src = result.violinplot;
        document.getElementById("boxplotImg").src = result.boxplot;
        document.getElementById("swarmplotImg").src = result.swarmplot;
        document.getElementById("countplotImg").src = result.countplot;

        


} catch (error) {
    console.error("Error fetching EDA results:", error);
}}
function report() {
    fetch('http://127.0.0.1:5000/profile')
    .then(response => {
       
            // Wait a bit to ensure the file is generated
            setTimeout(() => {
                window.location.href = "eda_report.html";
            }, 2000);
        
    })
    .catch(error => {
        console.error("Error fetching report:", error);
        alert("Error generating report!");
    });
}
function resetUploads() {
    fetch("http://127.0.0.1:5000/reset", { method: "POST" })
    .then(response => response.json())
    .then(data => {
        alert(data.message);  // Show success message
        console.log("Reset successful:", data);
        location.reload();  // Refresh the page
    })
    .catch(error => console.error("Error resetting uploads:", error));
}

