function addToMedicine(id,tenThuoc,donGia){

    fetch('/api/add-medicine',{
        method: 'post',
        body: JSON.stringify({
            'id':id,
            'tenThuoc':tenThuoc,
            'donGia':donGia
        }),
        headers:{
            'Content-Type':'application/json'
        }
    }).then(function (response ){
        return response.json()
    }).then(function (data){
        let counter = document.getElementById('count_medicine')
        counter.innerText =data.total_quantity
        number=data.total_quantity
    }).catch(function (err){
        console.error(err)
    })
}

function pay(){
    if(confirm('ban muon thanh toan chu')==true){
        fetch('/api/establishment',{
        method: 'post',
    }).then(res=> res.json()
    ).then (data=>{
        if(data.code == 200)
            location.reload()
    }).catch(err =>{console.error(err)
    })
    }

}
