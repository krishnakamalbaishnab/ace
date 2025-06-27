// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

// Initialize EmailJS
(function() {
    emailjs.init("MBy3dm0G1pb5A4I55");
})();

// Country card interactions
document.querySelectorAll('.country-card').forEach(card => {
    card.addEventListener('click', function() {
        const country = this.getAttribute('data-country');
        const countryNames = {
            'uk': 'United Kingdom',
            'germany': 'Germany',
            'usa': 'United States',
            'canada': 'Canada',
            'netherlands': 'Netherlands',
            'australia': 'Australia',
            'ireland': 'Ireland',
            'france': 'France',
            'sweden': 'Sweden',
            'new_zealand': 'New Zealand',
            'finland': 'Finland',
            'singapore': 'Singapore',
            'japan': 'Japan',
            'south_korea': 'South Korea',
            'italy': 'Italy'
        };
        
        // Scroll to contact form and pre-fill country
        const contactSection = document.querySelector('#contact');
        if (contactSection) {
            contactSection.scrollIntoView({ behavior: 'smooth' });
            
            // Pre-fill the country dropdown
            setTimeout(() => {
                const countrySelect = document.querySelector('select[name="target_country"]');
                if (countrySelect) {
                    countrySelect.value = country;
                }
            }, 500);
        }
        
        // Add visual feedback
        this.style.transform = 'scale(0.95)';
        setTimeout(() => {
            this.style.transform = 'scale(1)';
        }, 150);
    });
});

// Form submission handling
const form = document.getElementById('contactForm');
if (form) {
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Show loading state
        const submitButton = this.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.innerHTML;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Sending...';
        submitButton.disabled = true;

        // Prepare template parameters for main notification
        const notificationParams = {
            from_name: this.user_name.value,
            reply_to: this.user_email.value,
            current_education: this.current_education.value || 'Not specified',
            target_country: this.target_country.value,
            preferred_intakes: this.preferred_intakes.value || 'Not specified',
            message: this.message.value,
            to_email: 'help.aceassignment@gmail.com'
        };

        // Prepare template parameters for auto-reply
        const autoReplyParams = {
            to_name: this.user_name.value,
            to_email: this.user_email.value,
            target_country: this.target_country.value,
            preferred_intakes: this.preferred_intakes.value || 'Not specified',
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
                // Show success message
                showNotification('Thank you! Your message has been sent successfully. We\'ll get back to you within 24 hours.', 'success');
                form.reset();
            })
            .catch(function(error) {
                console.log('FAILED...', error);
                showNotification('There was an error sending your message. Please try again or contact us directly.', 'error');
            })
            .finally(function() {
                submitButton.innerHTML = originalButtonText;
                submitButton.disabled = false;
            });
    });
}

// Notification system
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification fixed top-20 right-4 z-50 p-4 rounded-lg shadow-lg max-w-md transform transition-all duration-300 translate-x-full`;
    
    // Set notification content based on type
    if (type === 'success') {
        notification.className += ' bg-green-500 text-white';
        notification.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-check-circle mr-2"></i>
                <span>${message}</span>
            </div>
        `;
    } else if (type === 'error') {
        notification.className += ' bg-red-500 text-white';
        notification.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-exclamation-circle mr-2"></i>
                <span>${message}</span>
            </div>
        `;
    } else {
        notification.className += ' bg-blue-500 text-white';
        notification.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-info-circle mr-2"></i>
                <span>${message}</span>
            </div>
        `;
    }
    
    // Add close button
    const closeButton = document.createElement('button');
    closeButton.innerHTML = '<i class="fas fa-times"></i>';
    closeButton.className = 'ml-2 hover:opacity-75 transition-opacity';
    closeButton.onclick = () => removeNotification(notification);
    notification.querySelector('div').appendChild(closeButton);
    
    // Add to page
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.classList.remove('translate-x-full');
    }, 100);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        removeNotification(notification);
    }, 5000);
}

function removeNotification(notification) {
    notification.classList.add('translate-x-full');
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 300);
}

// Mobile menu functionality
const mobileMenuButton = document.querySelector('.mobile-menu-button');
const mobileMenu = document.querySelector('.mobile-menu');

if (mobileMenuButton && mobileMenu) {
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
}

// Intersection Observer for animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-fade-in');
        }
    });
}, observerOptions);

// Observe elements for animation
document.addEventListener('DOMContentLoaded', () => {
    const animateElements = document.querySelectorAll('.country-card, .bg-white.p-8.rounded-xl');
    animateElements.forEach(el => {
        observer.observe(el);
    });
});

// Add CSS for animations
const style = document.createElement('style');
style.textContent = `
    .animate-fade-in {
        animation: fadeInUp 0.6s ease-out forwards;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .country-card {
        transition: all 0.3s ease;
    }
    
    .country-card:hover {
        transform: translateY(-5px);
    }
    
    .notification {
        z-index: 9999;
    }
`;
document.head.appendChild(style);

// Pricing plan interactions
document.querySelectorAll('#pricing button').forEach(button => {
    button.addEventListener('click', function() {
        const planName = this.closest('.bg-white, .bg-gradient-to-br').querySelector('h3').textContent;
        showNotification(`Thank you for your interest in the ${planName} plan! We'll contact you soon with more details.`, 'success');
        
        // Scroll to contact form
        setTimeout(() => {
            document.querySelector('#contact').scrollIntoView({ behavior: 'smooth' });
        }, 1000);
    });
});

// WhatsApp integration
function openWhatsApp() {
    const message = "Hi! I'm interested in studying abroad with ACE. Can you help me get started?";
    const whatsappUrl = `https://wa.me/447000000000?text=${encodeURIComponent(message)}`;
    window.open(whatsappUrl, '_blank');
}

// Add WhatsApp click handler if needed
document.addEventListener('DOMContentLoaded', () => {
    const whatsappElements = document.querySelectorAll('.fa-whatsapp');
    whatsappElements.forEach(element => {
        element.addEventListener('click', openWhatsApp);
    });
}); 