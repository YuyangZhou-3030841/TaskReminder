// Registration page form front-end validation

document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('registerForm');
    form.addEventListener('submit', function(e) {
      var errors = [];
      var username = form.elements['username'].value.trim();
      if (!username) {
        errors.push("Please enter your username.");
      }
      var email = form.elements['email'].value.trim();
      if (!email) {
        errors.push("Please enter your email address.");
      } else {
        if (!email.includes('@')) {
          errors.push("Email address must contain '@'.");
        }
        if (!email.includes('.com')) {
          errors.push("Email address must contain '.com'.");
        }
        var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
          errors.push("Please enter a valid email address.");
        }
      }
      var password1 = form.elements['password1'].value;
      if (!password1) {
        errors.push("Please enter your password.");
      }
      var password2 = form.elements['password2'].value;
      if (!password2) {
        errors.push("Please confirm your password.");
      }
      if (password1 && password2 && password1 !== password2) {
        errors.push("Passwords do not match.");
      }
      var phone = form.elements['phone'].value.trim();
      if (!phone) {
        errors.push("Please enter your telephone number.");
      } else if (!phone.startsWith('+')) {
        errors.push("Telephone number should start with '+'.");
      }
      var region = form.elements['region'].value;
      if (!region) {
        errors.push("Please select a region.");
      }
      if (errors.length > 0) {
        e.preventDefault();
        document.getElementById('clientErrors').innerHTML = errors.join("<br>");
      }
    });
  });
  