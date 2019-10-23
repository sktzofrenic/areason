var app = new Vue({
    el: '#coffee-store',
    delimiters: ['[[', ']]'],
    data: {
        coffeeItems: [{
                item: 'Guatemala',
                safeName: 'rwandanLight',
                description: 'A light body, single-origin Arabica bean with medium levels of acidity and chocolate tones.',
                price: 11.99,
                quantity: 1,
                option: 'Ground'
            },
            {
                item: 'Peru',
                safeName: 'brazilianDark',
                description: 'A rare, single-origin Arabica bean with a high range of complexity & balance that yields a smooth body and clean finish.',
                price: 11.99,
                quantity: 1,
                option: 'Ground'
            },
            {
                item: 'Colombia',
                safeName: 'zambianMedium',
                description: 'A full body, single-origin Arabica bean with an earthy aroma, low acidity and a light smokey finish.',
                price: 11.99,
                quantity: 1,
                option: 'Ground'
            }
        ],
        cart: []
    },
    methods: {
        checkout: function() {
            var vm = this;
            $.ajax({
                type: "POST",
                url: '/confirm/cart',
                data: JSON.stringify({
                    cart: vm.cart,
                    totals: {
                        shoppingTotal: vm.shoppingTotal,
                        shippingTotal: vm.shippingTotal,
                        taxTotal: vm.taxTotal,
                        stripeTotal: vm.stripeTotal,
                        total: vm.total
                    }
                }),
                success: function() {
                    window.location.href = '/confirm';
                },
                contentType: 'application/json',
            });
        },
        money: function(data) {
            return parseFloat(Math.round(data * 100) / 100).toFixed(2)
        },
        increment: function(item, index) {
            var vm = this;
            for (var i = 0; i < vm.cart.length; i++) {
                if (vm.cart[i] == item) {
                    vm.cart[i].quantity += 1
                }
            }
            for (var i = 0; i < vm.coffeeItems.length; i++) {
                if (vm.coffeeItems[i] == item) {
                    vm.coffeeItems[i].quantity += 1
                }
            }
        },
        decrement: function(item, index) {
            var vm = this;
            for (var i = 0; i < vm.cart.length; i++) {
                if (vm.cart[i] == item) {
                    vm.cart[i].quantity -= 1
                    if (vm.cart[i].quantity <= 0) {
                        vm.cart.splice(index, 1)
                    }
                }
            }
            for (var i = 0; i < vm.coffeeItems.length; i++) {
                if (vm.coffeeItems[i] == item) {
                    vm.coffeeItems[i].quantity -= 1
                    if (vm.coffeeItems[i].quantity < 0) {
                        vm.coffeeItems[i].quantity = 0
                    }
                }
            }
        },
        addToCart: function(item) {
            var vm = this;
            var objectToPush = {
                item: item.item,
                quantity: item.quantity,
                option: item.option,
                unitPrice: item.price,
            };
            var itemInCart = -1
            for (var i = 0; i < vm.cart.length; i++) {
                console.log(vm.cart[i].item, objectToPush.item, vm.cart[i].option, objectToPush.option)
                if (vm.cart[i].item == objectToPush.item && vm.cart[i].option == objectToPush.option) {
                    itemInCart = i
                }
            }
            if (itemInCart > -1) {
                vm.cart[itemInCart].quantity += 1
            } else {
                vm.cart.push(objectToPush)
            }
        }
    },
    computed: {
        shoppingTotal: function() {
            var vm = this;
            var total = 0
            for (var i = 0; i < vm.cart.length; i++) {
                total += vm.cart[i].unitPrice * vm.cart[i].quantity
            }
            return vm.money(total)
        },
        shippingTotal: function() {
            var vm = this;
            var total = 0
            for (var i = 0; i < vm.cart.length; i++) {
                total += vm.cart[i].quantity
            }
            return vm.money((total * 0.8) + 2.65) 
        },
        taxTotal: function() {
            return this.money(this.shoppingTotal * 0.08)
        },
        stripeTotal: function() {
            return +(this.total * 100)
        },
        total: function() {
            return this.money(Number(this.shoppingTotal) + Number(this.shippingTotal) + Number(this.taxTotal))
        }
    }
})
