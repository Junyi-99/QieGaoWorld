function abs(number){
    return number < 0 ? -number : number;
}

function list(url,page=1,type="user",el="#list",dataType="html"){
    $(el).html("");
    loading()
    $.ajax({
        type: "POST",
        url: url,
        data: {page:page,type:type},
        success: function(data){
            $(el).html(data);
            loading()
        },
        error:function(){
            loading(true)
        },
        dataType: "html"
      });
}
function loading(error=false){
    if($("#loading")[0].hidden){
        $("#loading")[0].hidden=false;
    }else{
        $("#loading")[0].hidden=true;
    }
    if(error){
        $("#loading")[0].hidden=true;
        $("#error")[0].hidden=false;
    }else{
        $("#error")[0].hidden=true;
    }
}
$(function(){
    $("#main_content").on("click",".qg-page",function () {
        var page=$(this).data("page");
        var url=$(this).data("url");
        var type=$(this).data("type");
        var el=$(this).data("el");
        var dataType=$(this).data("dataType");
        list(url,page,type,el,dataType);
    })
})
