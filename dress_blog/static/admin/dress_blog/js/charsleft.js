django.jQuery(document).ready(function() {
    var chl = django.jQuery('#charsleft');
    chl.siblings("textarea").attr("class", "fs14").keyup(function() {
        var n = 256 - django.jQuery(this).val().length;
	chl.html(n);
	if(n>=40) {
	    if(chl.attr("class").indexOf("c-green")!=0) chl.attr("class", "c-green")
	} else if(n>=0 && n<40) {
	    if(chl.attr("class").indexOf("c-blue")!=0) chl.attr("class", "c-blue")
	} else {
	    if(chl.attr("class").indexOf("c-red")!=0) chl.attr("class", "c-red")
	}
    });
});
