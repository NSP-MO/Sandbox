describe('Home Page Tests', () => {
    it('Loads the home page', () => {
      cy.visit('/')
      cy.contains('Popular Products').should('be.visible')
      cy.get('[data-testid="product-card"]').should('have.length.gt', 0)
    })
  
    it('Adds product to cart', () => {
      cy.visit('/')
      cy.get('[data-testid="add-to-cart"]').first().click()
      cy.contains('Added to cart!').should('be.visible')
      cy.get('[data-testid="cart-count"]').should('contain', '1')
    })
  })