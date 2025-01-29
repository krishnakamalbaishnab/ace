// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Initialize EmailJS
(function() {
    emailjs.init("MBy3dm0G1pb5A4I55");
})();

// Form submission handling
const form = document.getElementById('contactForm');
if (form) {
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Show loading state
        const submitButton = this.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.innerHTML;
        submitButton.innerHTML = 'Sending...';
        submitButton.disabled = true;

        // Prepare template parameters for main notification
        const notificationParams = {
            from_name: this.user_name.value,
            reply_to: this.user_email.value,
            subject: this.subject.value,
            word_count: this.word_count.value,
            deadline: this.deadline.value,
            message: this.message.value,
            to_email: 'help.aceassignment@gmail.com'
        };

        // Prepare template parameters for auto-reply
        const autoReplyParams = {
            to_name: this.user_name.value,
            to_email: this.user_email.value,
            subject: this.subject.value,
            word_count: this.word_count.value,
            deadline: this.deadline.value,
            message: this.message.value
        };

        // Send main email notification
        emailjs.send('service_ef4ba2l', 'template_9ouhuna', notificationParams)
            .then(function() {
                // Send auto-reply email
                return emailjs.send('service_ef4ba2l', 'template_wqzp9ub', autoReplyParams);
            })
            .then(function() {
                console.log('SUCCESS! Both emails sent');
                window.location.href = 'thanks.html';
            })
            .catch(function(error) {
                console.log('FAILED...', error);
                alert('There was an error sending your message. Please try again.');
                submitButton.innerHTML = originalButtonText;
                submitButton.disabled = false;
            });
    });
}

// Mobile menu functionality
const mobileMenuButton = document.querySelector('.mobile-menu-button');
const mobileMenu = document.querySelector('.mobile-menu');

mobileMenuButton.addEventListener('click', () => {
    mobileMenu.classList.toggle('hidden');
});

// Close mobile menu when clicking a link
document.querySelectorAll('.mobile-menu a').forEach(link => {
    link.addEventListener('click', () => {
        mobileMenu.classList.add('hidden');
    });
});

// Close mobile menu when clicking outside
document.addEventListener('click', (e) => {
    if (!mobileMenu.contains(e.target) && !mobileMenuButton.contains(e.target)) {
        mobileMenu.classList.add('hidden');
    }
});

// Close mobile menu when resizing to desktop view
window.addEventListener('resize', () => {
    if (window.innerWidth >= 768) { // 768px is Tailwind's md breakpoint
        mobileMenu.classList.add('hidden');
    }
}); 