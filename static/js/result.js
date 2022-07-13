$(document).ready(function(){
  getComment();
})
function getComment(){
  $.ajax({
    url:'./getComment',
    type:'GET',
    data:{},
    success:function(result){
      $(".comment-list").empty();
      console.log(result);
      let rows = result.msg
      for(let i=0; i<rows.length; i++){
        let comment = rows[i].comment_receive;
        comment = comment.replaceAll('\n','<br/>');
        let temp_html=`<article class="media">
                        <div class="media-left">
                          <figure class="image is-64x64">
                            <img src="https://bulma.io/images/placeholders/128x128.png" alt="Image">
                          </figure>
                        </div>
                        <div class="media-content">
                          <div class="content">
                            <p>
                              <strong>John Smith</strong> <small>@johnsmith</small> <small>31m</small>
                              <br/>
                              ${comment}
                            </p>
                            <div class="field is-grouped">
                              <p class="control"><button class="button is-link">Update</button></p>
                              <p class="control"><button class="button is-danger">Delete</button></p>
                            </div>
                          </div>
                        </div>
                      </article>`
        $(".comment-list").append(temp_html);
      }
    }
  })
}

$(".submit").on({
  click(){
    let $comment = $(".comment");
    if(!$.trim($comment.val())){
      alert('내용을 입력해주세요.');
      $comment.focus();
      return false;
    }
    $.ajax({
      url:'./commentAction',
      type:'POST',
      data:{ txt : $comment.val() },
      success:function(result){
        alert(result.msg);
        $comment.val("");
        getComment();
      }
    })
  }
})