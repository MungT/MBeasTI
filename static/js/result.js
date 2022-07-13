//실행하자마자 작동 됩니다
$(document).ready(function(){
  //댓글을 불러 오는 함수를 탑니다.
  getComment();
})

//댓글을 불러오는 함수입니다.
function getComment(){
  $.ajax({
    url:'./getComment',
    type:'GET',
    data:{now_mbti:$(".user_mbti").text()},/*페이지의 mbti를 넣어서 검색 조건에서 사용됩니다.*/
    success:function(result){
      $(".comment-list").empty();
      let rows = result.msg
      /*현 유저의 mbti입니다.*/
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
        /*지금 페이지의 mbit와 유저의 이름(계정) 확인해서 같으면 삭제/수정 버튼이 보입니다. */
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
      /*수정하기 위한 숨겨놓은 고유번호와 mbti를 초기화시킵니다.*/
      $(".modi-time, .modi-name").val("");
    }
  })
}

/*댓글 등록하는 버튼을 눌렀을 때 입니다. */
$(".submit").on({
  click(){
    let $comment = $(".comment");
    /* textarea에 글을 썼는지 공백인지 확인을 해서 공백이면 경고를 나타내고 정지를 시켜줍니다. */
    if(!$.trim($comment.val())){
      alert('내용을 입력해주세요.');
      $comment.focus();
      return false;
    }
    /* 유저 이름(계정)을 확앤해서 없으면 다시 로그인해라고 login페이지로 이동시킵니다.*/
    let userName = $(".user-name").data('name');
    if(!$.trim(userName)){
      alert('유저 정보가 없습니다.\n로그인 후 다시 진행 바랍니다.');
      window.location.reload('login.html');
    }
    /*등록버튼을 눌렀을때 수정인지 새로운 글을 쓰는지 판단합니다. true->새글, false->수정 */
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




// append로 동적으로 버튼이 만들어졌기 때문에 엘리먼트를 동적으로 선택할 수 있도록 함수 구현
$(document).on("click",'.del-btn',function(){
  if(confirm('삭제 하시겠습니까?')){
    let commentTime = $(this).parent().siblings(".val-time").data("time");
    $.ajax({
      url:'/commit-del',
      type:"POST",
      data:{valTime:commentTime},
      success:function(result){
        $(".comment").val("");
        alert(result.msg);
        getComment();/*삭제하고 완료후 다시 댓글을 부려줍니다*/
      }
    })
  }
})

// append로 동적으로 버튼이 만들어졌기 때문에 엘리먼트를 동적으로 선택할 수 있도록 함수 구현
/* update버튼을 눌러 해당하는 택스트를 textarea에 붙여 넣어줍니다*/
/* 어느것을 눌렸는지 알 수 있도록 고유번호도 함께 붙여줍니다(보이면 안되니까 hidden)으로 input타입을 숨김처리 합니다.*/
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



