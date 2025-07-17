namespace API.Requests.Products
{
    public class CreateProductRequest
    {
        public required string Name { get; set; }
        public required string Description { get; set; }
        public required string URL_Logo { get; set; }
        public required string api_key { get; set; }
        public required string assistant_id { get; set; }
        public required string realm_id { get; set; }
    }
}