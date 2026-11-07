document.addEventListener('DOMContentLoaded', function () {
    var contactForm = document.getElementById('contact-form');

    if (contactForm) {
        contactForm.addEventListener('submit', function (event) {
            event.preventDefault();
            var name = document.getElementById('name').value;
            var email = document.getElementById('email').value;
            var message = document.getElementById('message').value;

            if (name && email && message) {
                // Implement server-side logic to handle form submission.
                alert('Hello ' + name + ', your message has been sent. Thank you for contacting me!');
            } else {
                alert('Please fill out all required fields.');
            }
        });
    }
});
