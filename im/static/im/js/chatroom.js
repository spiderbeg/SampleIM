
// 心跳包，定时请求数据
$(function(){
    self.setInterval("clock()", 2000);//数据请求间隔
});
// 记录当前聊天对象
localStorage.user = 'a'; 
// 请求当前最新消息状态，--主要逻辑
function clock() {
    $.getJSON('/imapi/total/', {}, function(data) {
        // 从网页获取当前 登录用户名
        var sender = document.getElementById("username").innerHTML;
        // 添加用户列表
        add_users(data,sender);
        
        //获取当前聊天对象节点
        var ac = $('#username_list>li.activate'); 
        //根据节点获取当前选择用户 id maxpk 属性，
        var who = ac[0].getAttribute("id"); //当前聊天用户名 
        if (!ac[0].hasAttribute("maxpk")){// 还没有创建 maxpk 属性
            maxid = 0;
        }else{
            var maxid = ac[0].getAttribute("maxpk"); // 当前对象最新 pk 值
        }
        console.log('激活用户',who,'储存用户',localStorage.user);
        console.log('ok 最新消息',data);
        var tms = data.message_status; // 最新消息情况
        if (who==='first'){//生成当前用户键值
            var st = sender + '->' + 'firsttest';
        }else{
            var st = sender + '->' + who;
        }
        //当前聊天信息比较,
        // 1 第一次创建所有聊天信息, 2 而后查看有无新消息
        var acs = $('#username_list>li'); 
        for (let i=0, len=acs.length;i<len;i++){
            var who2 = acs[i].getAttribute("id"); 
            var maxpk2 = acs[i].getAttribute("maxpk"); 
            if (who2===sender){
                continue;
            }
            if (who2==='first'){//生成当前用户键值
                var st2 = sender + '->' + 'firsttest';
            }else{
                var st2 = sender + '->' + who2;
            }
            if (maxid === 0 && who === 'first'){//第一次数据请求,更新s所有数据
                if (who2==='first'){
                    //获取历史消息
                    // gethistory(who2,acs[i],data.message_status,style=0);
                    var new1 = tms[st2]-10;
                    get_newest(first=new1);
                }else{
                    gethistory(who2,acs[i],data.message_status,style=1);
                }
                //添加消息记录操作
                var user2 =  document.getElementById(who2);
                //设定最大值 pk; minpk 会在 gethistory 中设置
                user2.setAttribute("maxpk", tms[st2]);
            }else{
                var status = acs[i].children[1].children[1].children[0]; // 定位到 span 节点
                if(maxpk2<tms[st2] && who2 != who){ // 保证自己发的时候不会变色
                    status.setAttribute("class", "status orange");
                }else{
                    status.setAttribute("class", "status green");
                }
            }
        }

        //判断操作

        if(localStorage.user != who){ // 1 切换回
            console.log('群组节点显示修改',who);
            //修改当前聊天用户
            change_talker(who);
            //聊天页面自动滚动到最底部
            var d=$("#chat");
            d[0].scrollTop = d[0].scrollHeight;
        }
        if(maxid != tms[st] && maxid != 0){// 2 更新最新消息
            //更新最新消息, maxpk 会在 get_newest() 内添加
            get_newest();//滚动到底部在函数内实现
        }else{
            console.log('nothing change');
        }
        localStorage.user = who;//记录当前聊天对象

    })//getjson
}//clock()

//实现的函数

//改变聊天对象, 使当前显示对象显示出来
function change_talker(who){
    var li = $('#chat>li'); //获取节点
    for(var i=0, len=li.length; i<len;i++){
        if(li[i].getAttribute("name")===who){
            li[i].removeAttribute('style');
        }else{
            li[i].setAttribute('style','display:none;');
        }
    }
}

//这是比较函数，用户私聊按 pk 升序排列
function compare(p){ 
    return function(m,n){
        var a = m[p];
        var b = n[p];
        return a - b; //升序
    }
}

//添加管理用户列表
function add_users(data,sender){
    //获取前端用户列表
    var li3 = $('#user_list>ul>li');
    var ulist = [];
    for(let i=0, len=li3.length; i<len; i++){
        let liid = li3[i].getAttribute("id");
        ulist.push(liid);
    }
    console.log('ulist',ulist); // 用户列表
    // 接收后端返回用户列表
    var us = data.users;
    var ulist2 = ['first'];
    for (var i=0, len=us.length; i<len; i++){
        ulist2.push(us[i].username);
    }
    console.log('ulist2',ulist2);
     // 1 li3 前端用户列表节点 删除退出用户
    for(let i=0, len=li3.length; i<len; i++){
        let liid = li3[i].getAttribute("id");
        if(!ulist2.includes(liid)){
            li3[i].remove();
        }
    }
    // 用户有无消息指示灯
    var sh = '</h2> <h3> <span class="status green"></span> online </h3> </div> </li>';
    // 用户列表节点
    var chat2 = $('#user_list>ul');
    // 添加群组
    if(!ulist.includes('first')){
        var sb = '<li id="first" class="activate"> <img src="https://s3-us-west-2.amazonaws.com/s.cdpn.io/1940306/chat_avatar_01.jpg" alt="avatar"> <div>  <h2>';
        chat2.append(sb + 'first' + sh);
    }
    // ulist2 后端返回用户列表，添加新用户
    for (var i=0, len=us.length; i<len; i++){//隐藏用户自己的名字
        if(!ulist.includes(us[i].username)){
            if(us[i].username != sender){
                var sb = '<li id="' + us[i].username + '"> <img src="https://s3-us-west-2.amazonaws.com/s.cdpn.io/1940306/chat_avatar_01.jpg" alt="avatar"> <div>  <h2>';
                var sq = sb + us[i].username + sh;
                chat2.append(sq);
            }else{
                var sb = '<li style="display: none;" id="' + us[i].username + '"> <img src="https://s3-us-west-2.amazonaws.com/s.cdpn.io/1940306/chat_avatar_01.jpg" alt="avatar"> <div>  <h2>';
                var sq = sb + us[i].username + sh;
                chat2.append(sq);
            }
        }  
    };

    //比较用户是否相同，不变则不修改
    // if (ulist.toString() === ulist2.toString()){ //不变
    //     console.log('function: add_user -> 用户列表判断',ulist.toString() === ulist2.toString())
    // }else{

    //     var li2 = li3;
    //     console.log('获取的用户列表',li2);
    //     li2.remove();
    //     chat2 = $('#user_list>ul');
    //     var sb = '<li id="first" class="activate"> <img src="https://s3-us-west-2.amazonaws.com/s.cdpn.io/1940306/chat_avatar_01.jpg" alt="avatar"> <div>  <h2>';
    //     var sh = '</h2> <h3> <span class="status green"></span> online </h3> </div> </li>';
    //     chat2.append(sb + 'first' + sh);
    //     for (var i=0, len=us.length; i<len; i++){//隐藏用户自己的名字
    //         if(us[i].username != sender){
    //             var sb = '<li id="' + us[i].username + '"> <img src="https://s3-us-west-2.amazonaws.com/s.cdpn.io/1940306/chat_avatar_01.jpg" alt="avatar"> <div>  <h2>';
    //             var sq = sb + us[i].username + sh;
    //             chat2.append(sq);
    //         }else{
    //             var sb = '<li style="display: none;" id="' + us[i].username + '"> <img src="https://s3-us-west-2.amazonaws.com/s.cdpn.io/1940306/chat_avatar_01.jpg" alt="avatar"> <div>  <h2>';
    //             var sq = sb + us[i].username + sh;
    //             chat2.append(sq);
    //         }  
    //     };
    // }
}

// 发送群消息
// 1 获取 cookie 
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
// 2.1 发送群消息 私聊消息
function post_message(){
    // 信息预备，发送者及接收者
    // 发送方 获取用户名
    var sender = document.getElementById("username").innerHTML; // 获取网页内容
    // 接收方
    var ac = $('#username_list>li.activate'); //激活用户
    if(!ac[0].hasAttribute("id")){
        console.log("请等待");
        return false;
    }
    var who = ac[0].getAttribute("id"); // 获取当前选择用户
    // csrftoken
    var csrftoken = getCookie('csrftoken'); // csrf
    console.log(csrftoken)
    var messageinput = document.getElementById("inpumessage");
    var message = messageinput.value; //获取输入框内容
    console.log(sender, message)
    if(who === 'first'){
        $.ajax({
            type: "POST",
            url: '/imapi/groupmessage/',
            data: {'message':message,'sender':sender},
            headers:{"X-CSRFToken": csrftoken},
            success: function (newEnd) {
                console.log(newEnd);
            },
            error: function () {
                alert("There was an error, please try again!")
            }
            });
    }else{
        $.ajax({
            type: "POST",
            url: '/imapi/usermessage/',
            data: {'message':message,'sender':sender,'to':who},
            headers:{"X-CSRFToken": csrftoken},
            success: function (newEnd) {
                console.log(newEnd);
            },
            error: function () {
                alert("There was an error, please try again!")
            }
            });
    }  
    
    messageinput.value = "" //清空输入框
}   


//获取历史消息 
// 1 比较函数 用户 pk 值降序排列
function compare2(p){ //这是比较函数
    return function(m,n){
        var a = m[p];
        var b = n[p];
        return b - a; //降序
    }
}
// 2 请求发送
function gethistory(who=null,li=null,data=1,style=0){
    // 数据准备
    //获取当前用户名
    var sender = document.getElementById("username").innerHTML; // 获取网页内容
    //获取聊天对象
    if (who===null | li === null){//无参数输入时
        //获取聊天对象
        var lis = $('#username_list>li.activate'); //激活用户
        if(lis[0]!=null){//第一次获取不到，所以忽略第一次
            var who = lis[0].getAttribute("id"); // 获取当前选择用户
            var li = lis[0] //当前选中节点
        }
    }
     //激活用户 节点 li
    if(li.hasAttribute("id")){//第一次获取不到，所以忽略第一次
        var who = li.getAttribute("id"); // 获取当前选择用户
    }
    if(who==='first'){
        var type = 'group';
    }else{
        var type = 'personal'
    };
    if (li.hasAttribute("minpk")){
        var minpk = li.getAttribute("minpk");
        console.log('什么操作',minpk);
    }else{
        if (type=='group'){
            var s = sender + '->' + 'firsttest';
        }else{
            var s = sender + '->' + who;
        }
        var minpk = data[s] + 1;
        console.log('首次获取历史记录，应该在最新记录上加 1',data[s]);
    }
    console.log('历史记录传输消息',sender,who,type,minpk);
    //发送请求
    $.getJSON('/imapi/historymessage/', {"user1":sender,"user2":who,"type":type,"minpk":minpk}, function(history){
        // 加载历史消息
        handle_history(history, type,sender,who,li,style);
    });

}
// 第二步的历史数据处理
function handle_history(history, type, sender,who,li,style){
    console.log('历史消息',history);
    if (type === 'personal'){
        // 接收用户信息预备 1
        var uml2 = [];
        var um = history;
        var s1 = who + ' -> ' + sender;
        var s2 = sender + ' -> ' + who;
        console.log(s1, s2, um[s1], um[s2]);
        if(um[s1] != undefined){
            for(var i=0, len=um[s1].length; i<len; i++){
                uml2.push(um[s1][i]);
            }
        }
        if(um[s2] != undefined){
            for(var i=0, len=um[s2].length; i<len; i++){
                uml2.push(um[s2][i]);
            }
        }
        uml2.sort(compare2("pk"));
        console.log('用户信息',uml2);
        if(uml2.length === 0){
            return false;
        }
        
        var history = uml2;
    }else if(history.length===0){//已无用户群聊信息，退出
        return false;
    }
    //处理数据
    //加载历史记录
    chat = $("#main>ul"); //聊天内容
    for(var i=0, len=history.length; i<len; i++){
        var i2 = i;
        if (type==='group'){
            var sendtime = '<h3>'+ history[i2].timeg.substring(0,19) +'</h3>';
        }else{
            var sendtime = '<h3>'+ history[i2].timeu.substring(0,19) +'</h3>';
        }
        
        var senduser = ' <h2>' + history[i2].sender + '</h2>';
        var sendmessage = '<div class="message">' + escapeHtml(history[i2].message) + '</div>';
        // console.log('h history 0');
        if (style===0){
            // console.log('h history 1');
            if(history[i2].sender===sender){
                // console.log('h history 2');
                var s = '<li name=' + who +' class="me"> <div class="entete"> <span class="status blue"></span>' + senduser + sendtime + '</div> <div class="triangle"></div>' + sendmessage + '</li>'
            }else{
                // console.log('h history 3');
                var s = '<li name=' + who +' class="you"> <div class="entete"> <span class="status green"></span>' + senduser + sendtime + '</div> <div class="triangle"></div>' + sendmessage + '</li>'
            }
            // 添加内容，这是 jquery 写法 https://www.w3school.com.cn/jquery/jquery_dom_add.asp
            //另外还有 DOM 的写法 -搜索-js 修改节点
            $('#history').after(s);
        }else if(style===1){ //添加用户信息
            if(history[i2].sender===sender){
                var s = '<li style="display: none;" name=' + who +' class="me"> <div class="entete"> <span class="status blue"></span>' + senduser + sendtime + '</div> <div class="triangle"></div>' + sendmessage + '</li>'
            }else{
                var s = '<li style="display: none;" name=' + who +' class="you"> <div class="entete"> <span class="status green"></span>' + senduser + sendtime + '</div> <div class="triangle"></div>' + sendmessage + '</li>'
            }
            // 添加内容，这是 jquery 写法 https://www.w3school.com.cn/jquery/jquery_dom_add.asp
            //另外还有 DOM 的写法 -搜索-js 修改节点
            $('#history').after(s);
        }
        
    };
    console.log(history.length)
    console.log('历史消息序号',history[0].pk,history[history.length-1].pk);
    li.setAttribute("minpk", history[history.length-1].pk);//记录最小  pK
}

// 添加最新消息
function get_newest(first=0){
    // 数据准备
    //获取当前用户名
    var sender = document.getElementById("username").innerHTML; // 获取网页内容
    //获取聊天对象
    var ac = $('#username_list>li.activate'); //激活用户
    if(ac[0].hasAttribute("id")){//第一次获取不到，所以忽略第一次
        var who = ac[0].getAttribute("id"); // 获取当前选择用户
    }
    if(who==='first'){
        var type = 'group';
    }else{
        var type = 'personal';
    };
    var maxpk = ac[0].getAttribute("maxpk");
    if(first!=0){//第一次加载
        maxpk = first;
    }
    console.log('最新传输消息 maxpx',sender,who,type,maxpk);
    //发送请求
    $.getJSON('/imapi/newestmessage/', {"user1":sender,"user2":who,"type":type,"maxpk":maxpk}, function(newest){
        // 加载最新消息
        console.log('newest 最新',newest)
        handle_newest(newest,type,sender,who,ac,first);
        //聊天页面自动滚动到最底部
        var d=$("#chat");
        d[0].scrollTop = d[0].scrollHeight;
    });
}
// 添加最新消息
function handle_newest(newest,type,sender,who,ac,first){
    console.log('最新消息',newest);
    if (type === 'personal'){//整理用户最新消息
        // 接收用户信息预备 1
        var uml2 = [];
        var um = newest;
        var s1 = who + ' -> ' + sender;
        var s2 = sender + ' -> ' + who;
        console.log(s1, s2, um[s1], um[s2]);
        if(um[s1] != undefined){
            for(var i=0, len=um[s1].length; i<len; i++){
                uml2.push(um[s1][i]);
            }
        }
        if(um[s2] != undefined){
            for(var i=0, len=um[s2].length; i<len; i++){
                uml2.push(um[s2][i]);
            }
        }
        uml2.sort(compare("pk"));
        console.log('用户信息',uml2);
        if(uml2.length === 0){
            return false;
        }
        
        var newest = uml2;
    }else if(newest.length===0){//已无用户群聊信息，退出
        return false;
    }
    // 添加最新消息
    chat = $("#main>ul"); //聊天内容
    for(var i=0, len=newest.length; i<len; i++){
        var i2 = i;
        console.log('look out ',newest[i2])
        if (type==='group'){
            var sendtime = '<h3>'+ newest[i2].timeg.substring(0,19) +'</h3>';
        }else{
            var sendtime = '<h3>'+ newest[i2].timeu.substring(0,19) +'</h3>';
        }
        
        var senduser = ' <h2>' + newest[i2].sender + '</h2>';
        var sendmessage = '<div class="message">' + escapeHtml(newest[i2].message) + '</div>';
        if(newest[i2].sender===sender){
            var s = '<li name= '+ who +' class="me"> <div class="entete"> <span class="status blue"></span>' + senduser + sendtime + '</div> <div class="triangle"></div>' + sendmessage + '</li>'
        }else{
            var s = '<li name= '+ who +' class="you"> <div class="entete"> <span class="status green"></span>' + senduser + sendtime + '</div> <div class="triangle"></div>' + sendmessage + '</li>'
        }
        chat.append(s);
    };
    ac[0].setAttribute("maxpk", newest[newest.length-1].pk);//记录最大  pK
    if (first!=0){
        ac[0].setAttribute("minpk", newest[0].pk);//记录最大  pK
    }
}

//点击改变聊天对象颜色
$(document).ready(function(){// jquery 写法，页面加载完毕后执行
    document.getElementById("username_list").addEventListener("click", someFunction);
});
function someFunction(event) {
    var user =  document.getElementById(event.target.id);
    if(user != null && event.target.id != "username_list"){ //确保只点击用户
        var li3 = $('#user_list>ul>li');
        for(var i=0, len=li3.length; i<len; i++){
            li3[i].setAttribute("class", "deactivate");
        }
        console.log(event.target.id);
        
        user.setAttribute("class", "activate");
        console.log(user);
        }
}
// html 标签转移函数
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
// //检测页面关闭, 暂时不考虑
// window.addEventListener("beforeunload", function (e) {
//     $.getJSON('/imapi/groupmgpk/', {}, function(history){
//         console.log('are you ok ', history)
//     })
//     console.log('llllllllllllllllllllllll');
//     var confirmationMessage = "\o/";
//     (e || window.event).returnValue = confirmationMessage; //Gecko + IE
//     return confirmationMessage;                            //Webkit, Safari, Chrome
//   });


