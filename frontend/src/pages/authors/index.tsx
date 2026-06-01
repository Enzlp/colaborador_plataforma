import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import LoadingAuthor from './LoadingAuthor';
import { Building, MapPin, BookOpen, Award, ExternalLink, User } from "lucide-react";
import AuthorWorks from "./AuthorWorks";

interface Author {
  id: string;
  orcid?: string;
  display_name: string;
  display_name_alternatives: string[];
  works_count: number;
  cited_by_count: number;
  last_known_institution: string; 
  works_api_url: string;
  updated_date: Date;
}

interface Institution {
  id: string;
  display_name: string;
  homepage_url: string;
  country_code: string;
}


export default function Authors() {
  const latamCountryCodes: { [key: string]: string } = {
    AR: "Argentina", BO: "Bolivia", BR: "Brazil", CL: "Chile",
    CO: "Colombia", CR: "Costa Rica", CU: "Cuba", DO: "Dominican Republic",
    EC: "Ecuador", GT: "Guatemala", HN: "Honduras", MX: "Mexico",
    NI: "Nicaragua", PA: "Panama", PE: "Peru", PR: "Puerto Rico",
    PY: "Paraguay", SV: "El Salvador", UY: "Uruguay", VE: "Venezuela",
  };

  const { authorId } = useParams<{ authorId: string }>();
  const [authorInfo, setAuthorInfo] = useState<Author>();
  const [institutionName, setInstitutionName] = useState<string>("");
  const [institutionUrl, setInstitutionUrl] = useState<string>("");
  const [countryCode, setCountryCode] = useState<string>("");

  useEffect(() => {
    if (!authorId) return;

    const authorUrl = `https://openalex.org/${authorId}`;

    const timeoutId = setTimeout(() => {
      fetch(`http://127.0.0.1:8000/api/authors/?id=${authorUrl}`)
        .then((res) => res.json())
        .then(async (data: Author[]) => {
          const author = data[0];
          setAuthorInfo(author);

          if (author.last_known_institution) {
            try {
              const instRes = await fetch(
                `http://127.0.0.1:8000/api/institution/?id=${author.last_known_institution}`
              );
              const instData: Institution[] = await instRes.json();

              if (instData.length > 0) {
                setInstitutionName(instData[0].display_name);
                setInstitutionUrl(instData[0].homepage_url);
                setCountryCode(instData[0].country_code);
              } else {
                setInstitutionName("No disponible");
              }
            } catch {
              setInstitutionName("No disponible");
            }
          } else {
            setInstitutionName("No disponible");
          }
        });
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [authorId]);

  if (!authorInfo) return <LoadingAuthor />;

  

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-teal-50">
      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8">

        {/* Tarjeta de información */}
        <div className="bg-white rounded-xl sm:rounded-2xl shadow-xl border border-gray-100 p-5 sm:p-6 md:p-8 mb-6 sm:mb-8">
          <div className="flex flex-col sm:flex-row items-start gap-4 sm:gap-6 border-b border-gray-200 pb-5 sm:pb-6 mb-5 sm:mb-6">
            <div className="w-20 h-20 sm:w-24 sm:h-24 bg-gradient-to-br from-teal-100 to-cyan-100 rounded-xl sm:rounded-2xl flex items-center justify-center ring-2 sm:ring-4 ring-white shadow-lg flex-shrink-0">
              <User className="w-10 h-10 sm:w-12 sm:h-12 text-teal-600" />
            </div>
            <div className="flex-1 min-w-0 w-full">
              <h1 className="mb-2 text-xl sm:text-2xl md:text-3xl font-bold break-words">{authorInfo.display_name}</h1>
              {authorInfo.display_name_alternatives.length > 0 && (
                <div className="text-gray-600 mb-3 text-sm sm:text-base">
                  <span className="text-xs sm:text-sm text-gray-500">También conocido como: </span>
                  <span className="break-words">{authorInfo.display_name_alternatives.join(', ')}</span>
                </div>
              )}
              <div className="flex flex-wrap gap-2 sm:gap-3">
                <div className="inline-flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-3 py-1.5 bg-gradient-to-r from-teal-50 to-cyan-50 rounded-lg border border-teal-200" >
                  <Building className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-teal-600 flex-shrink-0" />
                  <a className="text-xs sm:text-sm text-teal-700 break-words" href={institutionUrl}>{institutionName}</a>
                </div>
                {countryCode && (
                  <div className="inline-flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-3 py-1.5 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-200">
                    <MapPin className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-purple-600 flex-shrink-0" />
                    <span className="text-xs sm:text-sm text-purple-700">{latamCountryCodes[countryCode]}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Stats y enlaces */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
            <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg sm:rounded-xl p-4 sm:p-5 border border-blue-100">
              <div className="flex items-center gap-2 sm:gap-3 mb-2">
                <div className="w-9 h-9 sm:w-10 sm:h-10 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-lg flex items-center justify-center flex-shrink-0">
                  <BookOpen className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
                </div>
                <div className="text-xs sm:text-sm text-gray-600">Publicaciones</div>
              </div>
              <div className="text-xl sm:text-2xl font-bold text-gray-900">{authorInfo.works_count.toLocaleString()}</div>
            </div>

            <div className="bg-gradient-to-br from-green-50 to-teal-50 rounded-lg sm:rounded-xl p-4 sm:p-5 border border-green-100">
              <div className="flex items-center gap-2 sm:gap-3 mb-2">
                <div className="w-9 h-9 sm:w-10 sm:h-10 bg-gradient-to-br from-green-500 to-teal-600 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Award className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
                </div>
                <div className="text-xs sm:text-sm text-gray-600">Citas</div>
              </div>
              <div className="text-xl sm:text-2xl font-bold text-gray-900">{authorInfo.cited_by_count.toLocaleString()}</div>
            </div>

            {authorInfo.orcid && (
              <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg sm:rounded-xl p-4 sm:p-5 border border-purple-100">
                <div className="flex items-center gap-2 mb-2">
                  <ExternalLink className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-purple-600 flex-shrink-0" />
                  <div className="text-xs sm:text-sm text-gray-600">ORCID</div>
                </div>
                <a
                  href={`https://orcid.org/${authorInfo.orcid}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-purple-700 hover:text-purple-800 hover:underline inline-flex items-center gap-1 break-all text-xs sm:text-sm"
                >
                  {authorInfo.orcid}
                  <ExternalLink className="w-3 h-3 flex-shrink-0" />
                </a>
              </div>
            )}

            <div className="bg-gradient-to-br from-orange-50 to-yellow-50 rounded-lg sm:rounded-xl p-4 sm:p-5 border border-orange-100">
              <div className="flex items-center gap-2 mb-2">
                <ExternalLink className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-orange-600 flex-shrink-0" />
                <div className="text-xs sm:text-sm text-gray-600">Perfil OpenAlex</div>
              </div>
              <a
                href={authorInfo.id}
                target="_blank"
                rel="noopener noreferrer"
                className="text-orange-700 hover:text-orange-800 hover:underline inline-flex items-center gap-1 text-xs sm:text-sm"
              >
                Ver perfil
                <ExternalLink className="w-3 h-3 flex-shrink-0" />
              </a>
            </div>
          </div>
        </div>

        {/* Works */}
        <AuthorWorks />
      </div>
    </div>
  );
}