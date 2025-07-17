using System;
using Xunit;
using Domain.Entities;
using Domain.Exceptions;

namespace Domain.UnitTests
{
    public class ProductTests
    {
        [Fact]
        public void Create_WithValidData_ShouldCreateProduct()
        {
            // Arrange
            var name = "Test Product";
            var description = "Test Description";
            var urlLogo = "https://example.com/logo.png";
            var apiKey = "1234567890";
            var assistantId = "1234567890";
            var realmId = "1234567890";

            // Act
            var product = new Product(name, description, urlLogo, apiKey, assistantId, realmId);

            // Assert
            Assert.Equal(name, product.Name);
            Assert.Equal(description, product.Description);
            Assert.Equal(urlLogo, product.URL_Logo);
            Assert.Equal(apiKey, product.api_key);
            Assert.Equal(assistantId, product.assistant_id);
            Assert.Equal(realmId, product.realm_id);
            Assert.NotEqual(Guid.Empty, product.Id);
            Assert.NotEqual(default, product.CreatedAt);
        }

        [Fact]
        public void Create_WithEmptyName_ShouldThrowException()
        {
            // Arrange
            var name = "";
            var description = "Test Description";
            var urlLogo = "https://example.com/logo.png";
            var apiKey = "1234567890";
            var assistantId = "1234567890";
            var realmId = "1234567890";

            // Act & Assert
            Assert.Throws<DomainException>(() => new Product(name, description, urlLogo, apiKey, assistantId, realmId));
        }

        [Fact]
        public void Create_WithEmptyURL_Logo_ShouldThrowException()
        {
            // Arrange
            var name = "Test Product";
            var description = "Test Description";
            var urlLogo = "";
            var apiKey = "1234567890";
            var assistantId = "1234567890";
            var realmId = "1234567890";

            // Act & Assert
            Assert.Throws<DomainException>(() => new Product(name, description, urlLogo, apiKey, assistantId, realmId));
        }

        [Fact]
        public void Create_WithEmptyApiKey_ShouldThrowException()
        {
            // Arrange
            var name = "Test Product";
            var description = "Test Description";
            var urlLogo = "https://example.com/logo.png";
            var apiKey = "";
            var assistantId = "1234567890";
            var realmId = "1234567890";

            // Act & Assert
            Assert.Throws<DomainException>(() => new Product(name, description, urlLogo, apiKey, assistantId, realmId));
        }

        [Fact]
        public void UpdateDetails_WithValidData_ShouldUpdateProduct()
        {
            // Arrange
            var product = new Product("Test Product", "Test Description", "https://example.com/logo.png", "1234567890", "1234567890", "1234567890");
            var newName = "Updated Product";
            var newDescription = "Updated Description";
            var newUrlLogo = "https://example.com/updated-logo.png";
            var newApiKey = "9876543210";
            var newAssistantId = "9876543210";
            var newRealmId = "9876543210";

            // Act
            product.UpdateDetails(newName, newDescription, newUrlLogo, newApiKey, newAssistantId, newRealmId);

            // Assert
            Assert.Equal(newName, product.Name);
            Assert.Equal(newDescription, product.Description);
            Assert.Equal(newUrlLogo, product.URL_Logo);
            Assert.Equal(newApiKey, product.api_key);
            Assert.Equal(newAssistantId, product.assistant_id);
            Assert.Equal(newRealmId, product.realm_id);
            Assert.NotEqual(default, product.UpdatedAt);
        }

        [Fact]
        public void UpdateDetails_WithEmptyName_ShouldThrowException()
        {
            // Arrange
            var product = new Product("Test Product", "Test Description", "https://example.com/logo.png", "1234567890", "1234567890", "1234567890");
            var newName = "";
            var newDescription = "Updated Description";
            var newUrlLogo = "https://example.com/logo.png";
            var newApiKey = "1234567890";
            var newAssistantId = "1234567890";
            var newRealmId = "1234567890";

            // Act & Assert
            Assert.Throws<DomainException>(() => product.UpdateDetails(newName, newDescription, newUrlLogo, newApiKey, newAssistantId, newRealmId));
        }
    }
}