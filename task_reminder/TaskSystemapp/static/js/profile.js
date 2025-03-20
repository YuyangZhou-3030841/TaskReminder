// User details page interaction logic

document.addEventListener('DOMContentLoaded', function() {
    // Add an event to each modification button that removes the disabled attribute of the corresponding form field when clicked and focuses the
    document.querySelectorAll('.edit-btn').forEach(function(button) {
      button.addEventListener('click', function() {
        var targetId = this.getAttribute('data-target');
        var field = document.getElementById(targetId);
        if (field) {
          field.removeAttribute('disabled');
          field.focus();
        }
      });
    });
    // Remove all disabled attributes before submitting the form in order to submit the data.
    var form = document.querySelector('form');
    if (form) {
      form.addEventListener('submit', function() {
        this.querySelectorAll('input[disabled], select[disabled]').forEach(function(field) {
          field.removeAttribute('disabled');
        });
      });
    }
  });
  