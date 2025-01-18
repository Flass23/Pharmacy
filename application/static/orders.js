// Handle switching between active and completed orders
document.querySelectorAll('.order-filters button').forEach(button => {
    button.addEventListener('click', () => {
        const filter = button.textContent.toLowerCase().replace(' ', '-') + '-orders';

        // Hide all orders sections
        document.querySelectorAll('.order-list').forEach(section => {
            section.style.display = 'none';
        });

        // Show the selected orders section
        document.getElementById(filter).style.display = 'block';

        // Update active button styling
        document.querySelectorAll('.order-filters button').forEach(b => {
            b.classList.remove('active');
        });

        button.classList.add('active');
    });
});

// Example to update the cart count dynamically (this could be done based on real data)
function updateCartCount(count) {
    document.querySelector('.cart-icon').textContent = `Cart (${count})`;
}

// Initial cart count update
updateCartCount(3); // Example cart with 3 items
