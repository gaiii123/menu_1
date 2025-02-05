$(document).ready(function() {
    $('#review_form').on('submit', function(e) {
        e.preventDefault();
        
        $.ajax({
            url: '/add_review',
            type: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                if (response.status === 'success') {
                    const stars = '★'.repeat(response.review.rating) + 
                                '☆'.repeat(5 - response.review.rating);
                    
                    const reviewHTML = `
                        <div class="review_item">
                            <div class="rating">${stars}</div>
                            <h4>${response.review.name}</h4>
                            <p>${response.review.comment}</p>
                            <small>Posted on: ${response.review.created_at}</small>
                            <hr>
                        </div>
                    `;
                    
                    $('#reviews_container').find('h3').after(reviewHTML);
                    $('#review_form')[0].reset();
                }
            },
            error: function() {
                alert('Error submitting review. Please try again.');
            }
        });
    });
});
document.addEventListener('DOMContentLoaded', function () {
    fetch('/get_reviews')
        .then(response => response.json())
        .then(reviews => {
            const reviewsContainer = document.getElementById('reviews_container');
            reviews.forEach(review => {
                const reviewElement = document.createElement('div');
                reviewElement.className = 'review_item';
                reviewElement.innerHTML = `
                    <div class="rating">${'★'.repeat(review.rating)}${'☆'.repeat(5 - review.rating)}</div>
                    <h4>${review.name}</h4>
                    <p>${review.comment}</p>
                    <small>Posted on: ${review.created_at}</small>
                    <hr>
                `;
                reviewsContainer.appendChild(reviewElement);
            });
        });
});