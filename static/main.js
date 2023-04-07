function fillQuestion(question) {
    document.querySelector('input[name="question"]').value = question;
  }

function showLoadingIndicator() {
    const loadingIndicator = document.getElementById('loading-indicator');
    loadingIndicator.style.display = 'block';
  }
  
  function submitForm() {
    const form = document.getElementById('playlist-form');
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      showLoadingIndicator();
      form.submit();
    });
  }
  
  document.addEventListener('DOMContentLoaded', () => {
    submitForm();
  });
  