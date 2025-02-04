export default function SearchResultCard({ result }) {
    const { title, snippet, link, image_url } = result;
  
    return (
      <div className="border border-gray-300 dark:border-gray-700 p-4 rounded shadow-sm">
        <h3 className="font-semibold text-lg mb-1">
          <a
            href={link}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 dark:text-blue-400 hover:underline"
          >
            {title}
          </a>
        </h3>
        <p className="text-sm mb-2">{snippet}</p>
        {image_url && (
          <div className="mt-2">
            {/* Next.js Image is nice, but we can do a basic img for simplicity */}
            <img
              src={image_url}
              alt={title}
              className="max-w-xs object-cover rounded"
            />
          </div>
        )}
      </div>
    );
  }
  