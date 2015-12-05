$(document).ready(function() {
    $('.add-service-form').submit(function(evt) {
        event.preventDefault();

        $.ajax({
            type: 'POST',
            data: $(this).serialize(),
            dataType: 'JSON',
            success: function(res) {
                if (res.error) {
                    console.log(res.message);
                } else {
                    window.location.replace('/');
                }
            }
        });
    });
});