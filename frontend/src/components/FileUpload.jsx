import {
  useRef,
  useState,
} from "react";

import {
  FileText,
  FileSpreadsheet,
  UploadCloud,
  CheckCircle2,
  X,
} from "lucide-react";


function FileUpload({
  title,
  description,
  type = "pdf",
  accept,
  file,
  onChange,
}) {

  const inputRef = useRef(null);

  const [
    dragging,
    setDragging
  ] = useState(false);


  const Icon =
    type === "excel"
      ? FileSpreadsheet
      : FileText;


  function seleccionarArchivo(
    archivo
  ) {

    if (!archivo) {
      return;
    }

    onChange(archivo);

  }


  function handleDrop(event) {

    event.preventDefault();

    setDragging(false);

    const archivo =
      event.dataTransfer.files[0];

    seleccionarArchivo(
      archivo
    );

  }


  return (

    <div className="upload-section">

      <div className="section-heading">

        <div className="section-icon">

          <Icon size={20} />

        </div>

        <div>

          <h3>
            {title}
          </h3>

          <p>
            {description}
          </p>

        </div>

      </div>


      {!file ? (

        <div
          className={
            `upload-box ${
              dragging
                ? "upload-box-dragging"
                : ""
            }`
          }
          onClick={() =>
            inputRef.current?.click()
          }
          onDragOver={(event) => {

            event.preventDefault();

            setDragging(true);

          }}
          onDragLeave={() =>
            setDragging(false)
          }
          onDrop={handleDrop}
        >

          <UploadCloud
            size={32}
          />

          <strong>
            Arrastra tu archivo aquí
          </strong>

          <span>
            o haz clic para seleccionarlo
          </span>

          <button
            type="button"
            className="upload-button"
          >
            Seleccionar archivo
          </button>

        </div>

      ) : (

        <div className="selected-file">

          <div className="selected-file-icon">

            <Icon size={23} />

          </div>

          <div className="selected-file-info">

            <strong>
              {file.name}
            </strong>

            <span>

              {(
                file.size /
                1024 /
                1024
              ).toFixed(2)} MB

            </span>

          </div>


          <CheckCircle2
            className="file-ok"
            size={21}
          />


          <button
            type="button"
            className="remove-file"
            onClick={() =>
              onChange(null)
            }
          >

            <X size={18} />

          </button>

        </div>

      )}


      <input
        ref={inputRef}
        hidden
        type="file"
        accept={accept}
        onChange={(event) =>
          seleccionarArchivo(
            event.target.files[0]
          )
        }
      />

    </div>
  );
}

export default FileUpload;