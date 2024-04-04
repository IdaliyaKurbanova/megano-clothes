var mix = {
	methods: {
		submitPayment() {
			console.log('qweqwewqeqweqw')
			const orderId = location.pathname.startsWith('/payment/')
				? Number(location.pathname.replace('/payment/', '').replace('/', ''))
				: null

			// this.number is always empty, so we get it using id
			const number = document.getElementById("numero1").value
			this.postData(`/api/payment/${orderId}/`, {
				name: this.name,
				number: number,
				year: this.year,
				month: this.month,
				code: this.code
			})
				.then(() => {
					alert('Успешная оплата')
					this.number = ''
					this.name = ''
					this.year = ''
					this.month = ''
					this.code = ''
					location.assign('/')
				})
				.catch(() => {
					console.warn('Ошибка при оплате')
				})
		}
	},
	data() {
		return {
			number: '',
			month: '',
			year: '',
			name: '',
			code: ''
		}
	}
}