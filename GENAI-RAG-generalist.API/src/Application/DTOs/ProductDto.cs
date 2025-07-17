using System;

namespace Application.DTOs
{
    public class ProductDto
    {
        public Guid Id { get; set; }
        public required string Name { get; set; }
        public required string Description { get; set; }
        public required string URL_Logo { get; set; }
        public required string api_key { get; set; }
        public required string assistant_id { get; set; }
        public required string realm_id { get; set; }
        public decimal Price { get; set; }
        public int Stock { get; set; }
        public DateTime CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }
    }
}