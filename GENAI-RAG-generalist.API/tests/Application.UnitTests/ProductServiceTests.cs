using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Application.DTOs;
using Application.Services;
using Domain.Entities;
using Domain.Interfaces;
using Moq;
using Xunit;

namespace Application.UnitTests
{
    public class ProductServiceTests
    {
        private readonly Mock<IProductRepository> _mockRepository;
        private readonly ProductService _service;

        public ProductServiceTests()
        {
            _mockRepository = new Mock<IProductRepository>();
            _service = new ProductService(_mockRepository.Object);
        }

        [Fact]
        public async Task GetById_WhenProductExists_ShouldReturnProduct()
        {
            // Arrange
            var productId = Guid.NewGuid();
            var product = new Product("Test Product", "Test Description", "https://example.com/logo.png", "1234567890", "1234567890", "1234567890");
            _mockRepository.Setup(r => r.GetByIdAsync(productId))
                .ReturnsAsync(product);

            // Act
            var result = await _service.GetByIdAsync(productId);

            // Assert
            Assert.NotNull(result);
            Assert.Equal(product.Id, result.Id);
            Assert.Equal(product.Name, result.Name);
            Assert.Equal(product.Description, result.Description);
            Assert.Equal(product.URL_Logo, result.URL_Logo);
            Assert.Equal(product.api_key, result.api_key);
            Assert.Equal(product.assistant_id, result.assistant_id);
            Assert.Equal(product.realm_id, result.realm_id);
        }

        [Fact]
        public async Task GetById_WhenProductDoesNotExist_ShouldReturnNull()
        {
            // Arrange
            var productId = Guid.NewGuid();
            _mockRepository.Setup(r => r.GetByIdAsync(productId))
                .ReturnsAsync((Product?)null);

            // Act
            var result = await _service.GetByIdAsync(productId);

            // Assert
            Assert.Null(result);
        }

        [Fact]
        public async Task GetAll_ShouldReturnAllProducts()
        {
            // Arrange
            var products = new List<Product>
            {
                new Product("Product 1", "Description 1", "https://example.com/logo.png", "1234567890", "1234567890", "1234567890"),
                new Product("Product 2", "Description 2", "https://example.com/logo.png", "1234567890", "1234567890", "1234567890")
            };
            _mockRepository.Setup(r => r.GetAllAsync())
                .ReturnsAsync(products);

            // Act
            var result = await _service.GetAllAsync();

            // Assert
            Assert.NotNull(result);
            Assert.Equal(2, result.Count());
        }

        [Fact]
        public async Task Create_ShouldCreateProduct()
        {
            // Arrange
            var name = "Test Product";
            var description = "Test Description";
            var urlLogo = "https://example.com/logo.png";
            var apiKey = "1234567890";
            var assistantId = "1234567890";
            var realmId = "1234567890";

            _mockRepository.Setup(r => r.AddAsync(It.IsAny<Product>()))
                .ReturnsAsync((Product p) => p);

            // Act
            var result = await _service.CreateAsync(name, description, urlLogo, apiKey, assistantId, realmId);

            // Assert
            Assert.NotNull(result);
            Assert.Equal(name, result.Name);
            Assert.Equal(description, result.Description);
            Assert.Equal(urlLogo, result.URL_Logo);
            Assert.Equal(apiKey, result.api_key);
            Assert.Equal(assistantId, result.assistant_id);
            Assert.Equal(realmId, result.realm_id);
            _mockRepository.Verify(r => r.AddAsync(It.IsAny<Product>()), Times.Once);
        }

        [Fact]
        public async Task Update_WhenProductExists_ShouldUpdateProduct()
        {
            // Arrange
            var productId = Guid.NewGuid();
            var product = new Product("Test Product", "Test Description", "https://example.com/logo.png", "1234567890", "1234567890", "1234567890");
            _mockRepository.Setup(r => r.GetByIdAsync(productId))
                .ReturnsAsync(product);

            // Act
            await _service.UpdateAsync(productId, "Updated Name", "Updated Description", "https://example.com/logo.png", "1234567890", "1234567890", "1234567890");

            // Assert
            _mockRepository.Verify(r => r.UpdateAsync(It.IsAny<Product>()), Times.Once);
        }

        [Fact]
        public async Task Update_WhenProductDoesNotExist_ShouldThrowException()
        {
            // Arrange
            var productId = Guid.NewGuid();
            _mockRepository.Setup(r => r.GetByIdAsync(productId))
                .ReturnsAsync((Product?)null);

            // Act & Assert
            await Assert.ThrowsAsync<Exception>(() =>
                _service.UpdateAsync(productId, "Updated Name", "Updated Description", "https://example.com/logo.png", "1234567890", "1234567890", "1234567890"));
        }

        [Fact]
        public async Task Delete_ShouldDeleteProduct()
        {
            // Arrange
            var productId = Guid.NewGuid();

            // Act
            await _service.DeleteAsync(productId);

            // Assert
            _mockRepository.Verify(r => r.DeleteAsync(productId), Times.Once);
        }
    }
}