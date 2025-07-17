using System.Net;
using System.Net.Http.Json;
using Application.DTOs;
using Application.Services;
using Controller.UnitTests.Base;
using FluentAssertions;
using Microsoft.AspNetCore.Mvc.Testing;
using Moq;

namespace Controller.UnitTests;

public class ProductsControllerTests : ControllerTestBase
{
    private readonly Mock<ProductService> _productServiceMock;
    private readonly string _baseUrl = "/api/products";

    public ProductsControllerTests()
    {
        _productServiceMock = MockRepository.Create<ProductService>();
    }

    [Fact]
    public async Task GetAll_ShouldReturnOkWithProducts()
    {
        // Arrange
        var expectedProducts = new List<ProductDto>
        {
            new() { Id = Guid.NewGuid(), Name = "Product 1", Description = "Description 1", Price = 10, Stock = 5 },
            new() { Id = Guid.NewGuid(), Name = "Product 2", Description = "Description 2", Price = 20, Stock = 10 }
        };
        _productServiceMock.Setup(x => x.GetAllAsync())
            .ReturnsAsync(expectedProducts);

        // Act
        var response = await Client.GetAsync(_baseUrl);

        // Assert
        response.Should().BeSuccessful();
        var result = await response.Content.ReadFromJsonAsync<List<ProductDto>>();
        result.Should().BeEquivalentTo(expectedProducts);
        VerifyAll();
    }

    [Fact]
    public async Task GetById_WhenProductExists_ShouldReturnOkWithProduct()
    {
        // Arrange
        var id = Guid.NewGuid();
        var expectedProduct = new ProductDto { Id = id, Name = "Product", Description = "Description", Price = 10, Stock = 5 };
        _productServiceMock.Setup(x => x.GetByIdAsync(id))
            .ReturnsAsync(expectedProduct);

        // Act
        var response = await Client.GetAsync($"{_baseUrl}/{id}");

        // Assert
        response.Should().BeSuccessful();
        var result = await response.Content.ReadFromJsonAsync<ProductDto>();
        result.Should().BeEquivalentTo(expectedProduct);
        VerifyAll();
    }

    [Fact]
    public async Task GetById_WhenProductDoesNotExist_ShouldReturnNotFound()
    {
        // Arrange
        var id = Guid.NewGuid();
        _productServiceMock.Setup(x => x.GetByIdAsync(id))
            .ReturnsAsync((ProductDto)null);

        // Act
        var response = await Client.GetAsync($"{_baseUrl}/{id}");

        // Assert
        response.Should().HaveStatusCode(HttpStatusCode.NotFound);
        VerifyAll();
    }

    [Fact]
    public async Task Create_WithValidData_ShouldReturnCreated()
    {
        // Arrange
        var request = new CreateProductRequest
        {
            Name = "New Product",
            Description = "New Description",
            Price = 15,
            Stock = 10
        };
        var createdProduct = new ProductDto
        {
            Id = Guid.NewGuid(),
            Name = request.Name,
            Description = request.Description,
            Price = request.Price,
            Stock = request.Stock
        };
        _productServiceMock.Setup(x => x.CreateAsync(
            request.Name,
            request.Description,
            request.Price,
            request.Stock))
            .ReturnsAsync(createdProduct);

        // Act
        var response = await Client.PostAsJsonAsync(_baseUrl, request);

        // Assert
        response.Should().HaveStatusCode(HttpStatusCode.Created);
        var result = await response.Content.ReadFromJsonAsync<ProductDto>();
        result.Should().BeEquivalentTo(createdProduct);
        VerifyAll();
    }

    [Fact]
    public async Task Create_WithInvalidData_ShouldReturnBadRequest()
    {
        // Arrange
        var request = new CreateProductRequest
        {
            Name = "", // Invalid empty name
            Description = "Description",
            Price = -1, // Invalid negative price
            Stock = -1 // Invalid negative stock
        };

        // Act
        var response = await Client.PostAsJsonAsync(_baseUrl, request);

        // Assert
        response.Should().HaveStatusCode(HttpStatusCode.BadRequest);
        VerifyNoOtherCalls();
    }

    [Fact]
    public async Task Update_WhenProductExists_ShouldReturnNoContent()
    {
        // Arrange
        var id = Guid.NewGuid();
        var request = new UpdateProductRequest
        {
            Name = "Updated Product",
            Description = "Updated Description",
            Price = 25
        };
        _productServiceMock.Setup(x => x.UpdateAsync(
            id,
            request.Name,
            request.Description,
            request.Price))
            .Returns(Task.CompletedTask);

        // Act
        var response = await Client.PutAsJsonAsync($"{_baseUrl}/{id}", request);

        // Assert
        response.Should().HaveStatusCode(HttpStatusCode.NoContent);
        VerifyAll();
    }

    [Fact]
    public async Task Update_WhenProductDoesNotExist_ShouldReturnNotFound()
    {
        // Arrange
        var id = Guid.NewGuid();
        var request = new UpdateProductRequest
        {
            Name = "Updated Product",
            Description = "Updated Description",
            Price = 25
        };
        _productServiceMock.Setup(x => x.UpdateAsync(
            id,
            request.Name,
            request.Description,
            request.Price))
            .ThrowsAsync(new Exception("Product not found"));

        // Act
        var response = await Client.PutAsJsonAsync($"{_baseUrl}/{id}", request);

        // Assert
        response.Should().HaveStatusCode(HttpStatusCode.NotFound);
        VerifyAll();
    }




    [Fact]
    public async Task Delete_WhenProductExists_ShouldReturnNoContent()
    {
        // Arrange
        var id = Guid.NewGuid();
        _productServiceMock.Setup(x => x.DeleteAsync(id))
            .Returns(Task.CompletedTask);

        // Act
        var response = await Client.DeleteAsync($"{_baseUrl}/{id}");

        // Assert
        response.Should().HaveStatusCode(HttpStatusCode.NoContent);
        VerifyAll();
    }

    [Fact]
    public async Task Delete_WhenProductDoesNotExist_ShouldReturnNotFound()
    {
        // Arrange
        var id = Guid.NewGuid();
        _productServiceMock.Setup(x => x.DeleteAsync(id))
            .ThrowsAsync(new Exception("Product not found"));

        // Act
        var response = await Client.DeleteAsync($"{_baseUrl}/{id}");

        // Assert
        response.Should().HaveStatusCode(HttpStatusCode.NotFound);
        VerifyAll();
    }
}