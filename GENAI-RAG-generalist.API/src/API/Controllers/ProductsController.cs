using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Application.DTOs;
using Application.Services;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Http;
using API.Requests.Products; // Atualizado para refletir o novo namespace

namespace API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Produces("application/json")]
    public class ProductsController : ControllerBase
    {
        private readonly ProductService _productService;

        public ProductsController(ProductService productService)
        {
            _productService = productService;
        }

        /// <summary>
        /// Get all products
        /// </summary>
        [HttpGet]
        [ProducesResponseType(typeof(IEnumerable<ProductDto>), StatusCodes.Status200OK)]
        public async Task<ActionResult<IEnumerable<ProductDto>>> GetAll()
        {
            var products = await _productService.GetAllAsync();
            return Ok(products);
        }

        /// <summary>
        /// Get a product by id
        /// </summary>
        [HttpGet("{id}")]
        [ProducesResponseType(typeof(ProductDto), StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        public async Task<ActionResult<ProductDto>> GetById(Guid id)
        {
            var product = await _productService.GetByIdAsync(id);
            if (product == null)
                return NotFound();

            return Ok(product);
        }

        /// <summary>
        /// Create a new product
        /// </summary>
        [HttpPost]
        [ProducesResponseType(typeof(ProductDto), StatusCodes.Status201Created)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<ActionResult<ProductDto>> Create([FromBody] CreateProductRequest request)
        {
            try
            {
                var product = await _productService.CreateAsync(
                    request.Name,
                    request.Description,
                    request.URL_Logo,
                    request.api_key,
                    request.assistant_id,
                    request.realm_id);

                return CreatedAtAction(nameof(GetById), new { id = product.Id }, product);
            }
            catch (Exception ex)
            {
                return BadRequest(ex.Message);
            }
        }

        /// <summary>
        /// Update a product
        /// </summary>
        [HttpPut("{id}")]
        [ProducesResponseType(StatusCodes.Status204NoContent)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<IActionResult> Update(Guid id, [FromBody] UpdateProductRequest request)
        {
            try
            {
                await _productService.UpdateAsync(id, request.Name, request.Description, request.URL_Logo, request.api_key, request.assistant_id, request.realm_id);
                return NoContent();
            }
            catch (Exception ex)
            {
                if (ex.Message == "Product not found")
                    return NotFound();

                return BadRequest(ex.Message);
            }
        }

        /// <summary>
        /// Delete a product
        /// </summary>
        [HttpDelete("{id}")]
        [ProducesResponseType(StatusCodes.Status204NoContent)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        public async Task<IActionResult> Delete(Guid id)
        {
            await _productService.DeleteAsync(id);
            return NoContent();
        }
    }
}