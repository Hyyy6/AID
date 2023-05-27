var test_var = 1

// Open the rules modal
function openRulesModal() {
  const modal = document.getElementById('rules-modal');
  modal.style.display = 'block';
  const rulesEditor = document.getElementById('rules-editor');

  fetch('/diary/rules/get', {
    method: 'GET'
  })
    .then(response => {
      // console.log(response)
      ret = response.text()
      console.log(ret)
      return ret
    })
    .then(rules => {
      rulesEditor.value = rules
      console.log(rules)
    })
    .catch(error => {
      console.error('Error:', error);
    });
}

// Close the rules modal
function closeRulesModal() {
  const modal = document.getElementById('rules-modal');
  modal.style.display = 'none';
}

// Save the rules
function saveRules() {
  const rulesEditor = document.getElementById('rules-editor');
  const rules = rulesEditor.value;

  // Send the rules to the server using AJAX or fetch API
  // Here's an example using fetch:

  form = new FormData()
  form.append('file', rules)
  fetch('/diary/rules/set', {
    method: 'POST',
    body: form
  })
    .then(response => {
      console.log('good save')
      console.log(response)
    })
    .catch(error => {
      console.error('Error:', error);
    });
}

// Cancel any unsaved changes and close the rules modal
function cancelRules() {
  const rulesEditor = document.getElementById('rules-editor');
  // rulesEditor.value = '';

  closeRulesModal();
}

// Load the contents of a file into the rules editor
function loadFile(event) {
  const file = event.target.files[0];
  const reader = new FileReader();

  reader.onload = function (e) {
    const rulesEditor = document.getElementById('rules-editor');
    rulesEditor.value = e.target.result;
  };
}