document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('stringForm');

    form.addEventListener('submit', function (event) {
        event.preventDefault(); 

        const userInput = document.getElementById('userInput').value;
        const resultElement = document.getElementById('result');
        const uniqueValuesElement = document.getElementById('uniqueValues');
        const keysListElement = document.getElementById('keysList');
        var ele = document.querySelector('.extension');
        var scanButton = document.querySelector(".urlbutton")
        console.log(scanButton.innerText)
        setScanButtonState(true,scanButton);
        clearResults(resultElement,uniqueValuesElement,keysListElement)
        fetch('http://127.0.0.1:5000/', {
            method: 'POST',
            mode: "cors",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: userInput }),
        })
            .then(response => response.json())
            .then(data => {
                console.log('Response from Flask server:', data);
                ele.style.removeProperty("justify-content");
                const uniqueValuesCount = countUniqueValues(data);
                resultElement.innerText = `WARNING: Detected ${Object.keys(data).length} Dark Patterns across ${uniqueValuesCount} unique categories on this website. click to see`;
                setScanButtonState(false,scanButton)
                resultElement.addEventListener('click', function () {
                    // Display the popup with unique values
                    displayUniqueValues(data,uniqueValuesElement,keysListElement);
                  });




            })
            .catch(error => {
                console.error('Error:', error);
            });
        // console.log('User Input:', userInput);

    });
});


function countUniqueValues(data) {
    // Use a Set to store unique values
    const uniqueValuesSet = new Set();

    // Iterate over the values in the response
    for (const key in data) {
        if (data.hasOwnProperty(key)) {
            const value = data[key];
            uniqueValuesSet.add(value);
        }
    }

    // Return the count of unique values
    return uniqueValuesSet.size;
}


function displayUniqueValues(data,uniqueValuesElement,keysListElement) {
    // Clear previous content
    uniqueValuesElement.innerHTML = '';
    keysListElement.innerHTML = '';

    // Create a Map to store unique values and their occurrences
    const uniqueValuesMap = new Map();

    // Iterate over the values in the response
    for (const key in data) {
      if (data.hasOwnProperty(key)) {
        const value = data[key];

        // Update the Map with value occurrences
        if (uniqueValuesMap.has(value)) {
          uniqueValuesMap.set(value, uniqueValuesMap.get(value) + 1);
        } else {
          uniqueValuesMap.set(value, 1);
        }
      }
    }

    // Display unique values with occurrences
    uniqueValuesMap.forEach((occurrences, value) => {
      const valueElement = document.createElement('div');
      valueElement.innerText = `${value}(${occurrences})`;
      
      // Add a click event listener to show keys when clicked
      valueElement.addEventListener('click', function () {
        displayKeysForValue(data, value,keysListElement);
      });

      uniqueValuesElement.appendChild(valueElement);
      valueElement.classList.add("DarkPatternTypes");
    });
  }

  function displayKeysForValue(data, selectedValue,keysListElement) {
    // Clear previous content
    keysListElement.innerHTML = '';

    // Iterate over the keys in the response and show keys for the selected value
    for (const key in data) {
      if (data.hasOwnProperty(key)) {
        const value = data[key];

        if (value === selectedValue) {
          const keyElement = document.createElement('div');
          keyElement.innerText = key;
          keysListElement.appendChild(keyElement);
          keyElement.classList.add("KeysOfDarkPattern")
        }
      }
    }
  }

  function setScanButtonState(isScanning,scanButton) {
    // Update button label based on the loading state
    scanButton.innerText = isScanning ? 'Scanning...' : 'SCAN';

    // Disable the button while scanning
    scanButton.disabled = isScanning;
  }
  function clearResults(resultElement,uniqueValuesElement,keysListElement){
   resultElement.innerText = ""
   uniqueValuesElement.innerText ="" 
   keysListElement.innerText =  ""
  }