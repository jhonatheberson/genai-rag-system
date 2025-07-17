using Application.DTOs;
using Domain.Entities;

namespace Application.Mappers
{
    public static class ProductMapper
    {
        public static ProductDto ToDto(Product product)
        {
            if (product == null)
                throw new ArgumentNullException(nameof(product));

            return new ProductDto
            {
                Id = product.Id,
                Name = product.Name,
                Description = product.Description,
                URL_Logo = product.URL_Logo,
                api_key = product.api_key,
                assistant_id = product.assistant_id,
                realm_id = product.realm_id,
                CreatedAt = product.CreatedAt,
                UpdatedAt = product.UpdatedAt
            };
        }

        public static IEnumerable<ProductDto> ToDto(IEnumerable<Product> products)
        {
            return products.Select(ToDto).ToList();
        }
    }
}