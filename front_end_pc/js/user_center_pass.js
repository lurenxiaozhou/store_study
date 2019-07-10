var vm = new Vue({
    el: '#app',
    data: {
        error_password: false,
        error_check_password: false,
        error_old_password : false,



        host: host,
        password: '',
        password1: '',
        password2: '',


    },
    methods:{
        // 原密码
        check_opwd: function (){
            var len = this.password.length;
            if(len<8||len>20){
                this.error_old_password = true;
            } else {
                this.error_old_password = false;
            }
        },
        // 新密码
        check_pwd: function (){
            var len = this.password1.length;
            if(len<8||len>20){
                this.error_password = true;
            } else {
                this.error_password = false;
            }
        },
        // 确认新密码
        check_cpwd: function (){
            if(this.password1!=this.password2) {
                this.error_check_password = true;
            } else {
                this.error_check_password = false;
            }
        },
        // 确定
        on_submit: function(){
            this.check_opwd();
            this.check_pwd();
            this.check_cpwd();
            if(this.error_password == false && this.error_check_password == false && this.error_old_password == false){
                axios.post(this.host + '/addpassword/', {

                        password: this.password,
                        password1: this.password1,
                        password2: this.password2,

                    }, {
                        responseType: 'json'
                    }).then(response => {
                        location.href = '/login.html';
                    }).catch(error=> {

                })
            }
        }
    }
})