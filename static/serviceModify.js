var SERVICE_TAGS = ['Nails', 'Tutoring', 'Childcare', 'Fashion', 'Beauty', 'Housing', 
                    'Housekeeping', 'Designated driving', 'Cleaning', 'Repair and Maintainance',
                    'Construction', 'Education', 'Entertainment', 'Personal Grooming', 'Public Utility',
                    'Risk Management', 'Social Services', 'Transport'
 ]

$(document).ready(function(){

	$("#service_tags").autocomplete({
             minLength: 0,
             source: function( request, response ) {
                 response( $.ui.autocomplete.filter(
                     SERVICE_TAGS, extractLast( request.term ) ) );
             },
             focus: function() {
                 return false;
             },
            select: function( event, ui ) {
                var terms = split( this.value );
                terms.pop();
                terms.push( ui.item.value );
                terms.push( "" );
                this.value = terms.join( ", " );
                return false;
            }
        });
});

function split( val ) {
      return val.split( /,\s*/ );
    }
    function extractLast( term ) {
      return split( term ).pop();
    }