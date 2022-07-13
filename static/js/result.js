$(document).ready(function(){
  getComment();
})
function getComment(){
  $.ajax({
    url:'./getComment',
    type:'GET',
    data:{now_mbti:$(".user_mbti").text()},
    success:function(result){
      $(".comment-list").empty();
      let rows = result.msg
      let nowUserName = $(".user-name").data('name');
      for(let i=(rows.length-1); i>-1; i--){
        let dataTime = rows[i].data_time;
        let userName = rows[i].user_name;
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
                              <strong>${userName}</strong>
                              <br/>
                              ${comment}
                            </p>`
        if(nowUserName===userName){
          temp_html += `<div class="field is-grouped">
                          <p class="control"><button class="button is-link up-btn">Update</button></p>
                          <p class="control"><button class="button is-danger del-btn">Delete</button></p>
                          <input type="hidden" class="val-time" data-time="${dataTime}"/>
                        </div>`
        }

        temp_html+=`</div>
                  </div>
                </article>`
        $(".comment-list").append(temp_html);
      }
    },complete:function(){
      $(".modi-time, .modi-name").val("");
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
    let userName = $(".user-name").data('name');
    if(!$.trim(userName)){
      alert('유저 정보가 없습니다.\n로그인 후 다시 진행 바랍니다.');
      window.location.reload('login.html');
    }
    if(!$(".modi-time").val()){
      $.ajax({
      url:'./commentAction',
      type:'POST',
      data:{ txt : $comment.val(), user : userName, now_mbti: $(".user_mbti").text() },
      success:function(result){
        alert(result.msg);
        $comment.val("");
        getComment();
      }
    })
    }else{
      $.ajax({
        url:'./commentModify',
        type:'POST',
        data:{ txt: $comment.val(), user : userName, time : $(".modi-time").val() },
        success:function(result){
          alert(result.msg);
          $comment.val("");
          getComment();
        }
      })
    }
  }
})





$(document).on("click",'.del-btn',function(){
  if(confirm('삭제 하시겠습니까?')){
    let commentTime = $(this).parent().siblings(".val-time").data("time");
    $.ajax({
      url:'/commit-del',
      type:"POST",
      data:{valTime:commentTime},
      success:function(result){
        alert(result.msg);
        getComment();
      }
    })
  }
})

$(document).on("click",'.up-btn',function(){
  if(confirm('내용을 수정 하시겠습니까?')){
    let commentTime = $(this).parent().siblings(".val-time").data("time");
    $.ajax({
      url:'/commit-up',
      type:"POST",
      data:{valTime:commentTime},
      success:function(result){
        let info = result.msg;
        let comment = info.comment_receive;
        let time = info.data_time;
        let name = info.user_name;
        $(".comment").val(comment).focus();
        $(".modi-time").val(time);
        $(".modi-name").val(name);
        // getComment();
      }
    })
  }
})



